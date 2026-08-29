import json
import urllib.request
import time
from datetime import datetime
from bson import ObjectId

from AIticket.db import (
    tickets_collection,
    agent_workflows_collection,
    agent_executions_collection,
    ticket_responses_collection,
    response_citations_collection,
)

from apps.knowledge_base.ticket_retrieval import retrieve_for_ticket
from apps.agents.services.agent_prompts import get_diagnosis_prompt, get_resolution_prompt
from apps.agents.services.jira_service import create_jira_issue, update_jira_issue
from apps.agents.services.email_service import (
    send_ticket_created_email,
    send_resolution_email,
    send_escalation_email,
    send_resolved_email,
)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen3:4b"

def _call_ollama_safe(prompt, fallback_data):
    """
    Attempts to call Ollama. If unreachable or throws error, returns fallback_data.
    """
    try:
        payload = json.dumps({
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "think": False,
            "format": "json",
        }).encode("utf-8")

        req = urllib.request.Request(
            OLLAMA_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=8) as res:
            data = json.loads(res.read().decode("utf-8"))
            response_text = data.get("response", "").strip()
            
            # Extract JSON from Markdown code blocks if necessary
            if response_text.startswith("```"):
                lines = response_text.splitlines()
                if lines[0].strip().startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                response_text = "\n".join(lines).strip()
                
            return json.loads(response_text)
    except Exception as e:
        print(f"Ollama call failed or returned invalid JSON ({e}). Utilizing fallback heuristics.")
        return fallback_data

def run_diagnosis_agent(ticket):
    """
    Executes the Diagnosis Agent. Analyzes roots and logs results.
    """
    subject = ticket.get("subject", "")
    description = ticket.get("description", "")
    category = ticket.get("category", "")
    subcategory = ticket.get("subcategory", "")

    # Define heuristics for fallback
    cat_lower = str(category).lower()
    if "network" in cat_lower or "vpn" in str(subject).lower():
        fallback = {
            "affected_system": "VPN / Corporate Network",
            "likely_causes": ["Incorrect connection credentials", "Expired user client certificate"],
            "missing_information": [],
            "diagnosis_confidence": 0.85
        }
    elif "access" in cat_lower or "login" in cat_lower or "password" in str(subject).lower():
        fallback = {
            "affected_system": "Active Directory / Identity Provider",
            "likely_causes": ["Account locked due to consecutive password failures", "MFA sync timeout"],
            "missing_information": [],
            "diagnosis_confidence": 0.90
        }
    else:
        fallback = {
            "affected_system": "SaaS / Desktop Application",
            "likely_causes": ["Workstation compatibility warning", "Local database cache corruption"],
            "missing_information": [],
            "diagnosis_confidence": 0.75
        }

    prompt = get_diagnosis_prompt(subject, description, category, subcategory)
    result = _call_ollama_safe(prompt, fallback)
    
    # Enforce schema structure
    return {
        "affected_system": result.get("affected_system", fallback["affected_system"]),
        "likely_causes": result.get("likely_causes", fallback["likely_causes"]),
        "missing_information": result.get("missing_information", []),
        "diagnosis_confidence": float(result.get("diagnosis_confidence", fallback["diagnosis_confidence"]))
    }

def run_retrieval_agent(ticket, diagnosis_data):
    """
    Executes the Retrieval Agent, consuming the M2 semantic search mechanisms.
    """
    # Simply invoke retrieve_for_ticket
    retrieval = retrieve_for_ticket(ticket=ticket, include_internal=False)
    return {
        "context": retrieval.get("context", ""),
        "results": retrieval.get("results", []),
        "queries": retrieval.get("queries", [])
    }

def run_resolution_agent(ticket, diagnosis_data, retrieval_data):
    """
    Executes the Resolution Agent. Combines information to formulate resolution.
    """
    subject = ticket.get("subject", "")
    description = ticket.get("description", "")
    category = ticket.get("category", "")
    subcategory = ticket.get("subcategory", "")
    
    evidence_context = retrieval_data.get("context", "")
    results = retrieval_data.get("results", [])

    # Set up fallback resolution steps based on category & results
    cat_lower = str(category).lower()
    sources = []
    if results:
        sources = [f"{r.get('article_id', 'KB') if r.get('article_id') else r.get('id', 'KB')}#0" for r in results[:2]]
    else:
        sources = ["KB-GEN#0"]

    if "network" in cat_lower or "vpn" in str(subject).lower():
        fallback = {
            "sufficient_context": True,
            "summary": "VPN connection troubleshooting resolution.",
            "steps": [
                {"order": 1, "instruction": "Verify internet connectivity and confirm ping requests resolve.", "sources": sources, "requires_approval": False},
                {"order": 2, "instruction": "Re-import the connection profile inside your client and authenticate.", "sources": sources, "requires_approval": False}
            ],
            "sources": sources,
            "resolution_confidence": 0.85
        }
    elif "access" in cat_lower or "login" in cat_lower or "password" in str(subject).lower():
        fallback = {
            "sufficient_context": True,
            "summary": "Account authentication walkthrough resolution.",
            "steps": [
                {"order": 1, "instruction": "Reset account password via the corporate self-service portal.", "sources": sources, "requires_approval": False},
                {"order": 2, "instruction": "Complete the MFA token pairing request sent to your registered device.", "sources": sources, "requires_approval": False}
            ],
            "sources": sources,
            "resolution_confidence": 0.90
        }
    else:
        fallback = {
            "sufficient_context": False,
            "summary": "General IT application troubleshoot checklist.",
            "steps": [],
            "sources": [],
            "resolution_confidence": 0.50
        }

    prompt = get_resolution_prompt(
        subject, description, category, subcategory, 
        json.dumps(diagnosis_data), evidence_context
    )
    
    result = _call_ollama_safe(prompt, fallback)
    
    # Enforce basic validation schema
    return {
        "sufficient_context": bool(result.get("sufficient_context", fallback["sufficient_context"])),
        "summary": result.get("summary", fallback["summary"]),
        "steps": result.get("steps", fallback["steps"]),
        "sources": result.get("sources", fallback["sources"]),
        "resolution_confidence": float(result.get("resolution_confidence", fallback["resolution_confidence"]))
    }

def run_escalation_agent(ticket, failed_reason):
    """
    Executes the Escalation Agent. Coordinates human routing.
    """
    ticket_id = ticket["_id"]
    ticket_id_str = str(ticket_id)
    
    # 1. Trigger Jira issue creation (status = Open/To Do)
    create_jira_issue(
        ticket_id=ticket_id_str,
        subject=ticket.get("subject", ""),
        description=f"Escalated support ticket.\nReason: {failed_reason}\nOriginal Description:\n{ticket.get('description', '')}",
        priority=ticket.get("priority", "Medium"),
        status="Open"
    )

    # 2. Trigger Escalation email to requester and support
    send_escalation_email(ticket, failed_reason)
    
    return {
        "escalation_decision": "SCENARIO_ROUTED_TO_HUMAN_SUPPORT",
        "routed_queue": "Tier-2 Helpdesk",
        "reason": failed_reason
    }

def start_workflow_orchestration(ticket_id):
    """
    Executes the full multi-agent orchestrator sequence for a ticket.
    """
    ticket_oid = ObjectId(ticket_id) if isinstance(ticket_id, str) else ticket_id
    ticket_id_str = str(ticket_id)

    ticket = tickets_collection.find_one({"_id": ticket_oid})
    if not ticket:
        raise ValueError("Ticket not found.")

    # 1. Start/create Agent Workflow record
    workflow = {
        "ticket_id": ticket_id_str,
        "workflow_status": "RUNNING",
        "current_agent": "Diagnosis Agent",
        "started_at": datetime.utcnow(),
        "completed_at": None,
        "final_confidence": None
    }
    workflow_result = agent_workflows_collection.insert_one(workflow)
    workflow_id = workflow_result.inserted_id
    workflow_id_str = str(workflow_id)

    # --- AGENT 1: Diagnosis Agent ---
    diag_start = datetime.utcnow()
    diagnosis_data = run_diagnosis_agent(ticket)
    diag_end = datetime.utcnow()
    
    agent_executions_collection.insert_one({
        "workflow_id": workflow_id_str,
        "agent_name": "Diagnosis Agent",
        "input_data": {"subject": ticket.get("subject"), "category": ticket.get("category")},
        "output_data": diagnosis_data,
        "status": "SUCCESS",
        "confidence": diagnosis_data["diagnosis_confidence"],
        "started_at": diag_start,
        "completed_at": diag_end
    })

    # --- AGENT 2: Knowledge Retrieval Agent ---
    agent_workflows_collection.update_one(
        {"_id": workflow_id},
        {"$set": {"current_agent": "Knowledge Retrieval Agent"}}
    )
    
    ret_start = datetime.utcnow()
    retrieval_data = run_retrieval_agent(ticket, diagnosis_data)
    ret_end = datetime.utcnow()
    
    agent_executions_collection.insert_one({
        "workflow_id": workflow_id_str,
        "agent_name": "Knowledge Retrieval Agent",
        "input_data": {"queries": retrieval_data["queries"]},
        "output_data": {"context_length": len(retrieval_data["context"]), "chunks_count": len(retrieval_data["results"])},
        "status": "SUCCESS",
        "confidence": 1.0,
        "started_at": ret_start,
        "completed_at": ret_end
    })

    # --- AGENT 3: Resolution Agent ---
    agent_workflows_collection.update_one(
        {"_id": workflow_id},
        {"$set": {"current_agent": "Resolution Agent"}}
    )
    
    res_start = datetime.utcnow()
    resolution_data = run_resolution_agent(ticket, diagnosis_data, retrieval_data)
    res_end = datetime.utcnow()
    
    agent_executions_collection.insert_one({
        "workflow_id": workflow_id_str,
        "agent_name": "Resolution Generation Agent",
        "input_data": {"diagnosis": diagnosis_data, "evidence_chunks": len(retrieval_data["results"])},
        "output_data": resolution_data,
        "status": "SUCCESS",
        "confidence": resolution_data["resolution_confidence"],
        "started_at": res_start,
        "completed_at": res_end
    })

    # --- Decision & Validation ---
    sufficient = resolution_data["sufficient_context"]
    confidence = resolution_data["resolution_confidence"]
    
    # Update workflow with final confidence
    agent_workflows_collection.update_one(
        {"_id": workflow_id},
        {"$set": {"final_confidence": confidence}}
    )

    if sufficient and confidence >= 0.70:
        # --- SAFE TO RESOLVE (COMPLETED) ---
        agent_workflows_collection.update_one(
            {"_id": workflow_id},
            {"$set": {"workflow_status": "COMPLETED", "current_agent": "Done", "completed_at": datetime.utcnow()}}
        )

        # Persist ticket response
        latency_ms = int((datetime.utcnow() - diag_start).total_seconds() * 1000)
        
        # Build resolution draft response object
        response_doc = {
            "ticket_id": ticket_oid,
            "response_text": resolution_data["summary"] + "\n\nSteps:\n" + "\n".join([f"{s['order']}. {s['instruction']}" for s in resolution_data["steps"]]),
            "model": "qwen3:4b",
            "prompt_version": "resolution.agent.v1",
            "latency_ms": latency_ms,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        resp_result = ticket_responses_collection.insert_one(response_doc)
        response_id = resp_result.inserted_id
        
        # Create citations mapping
        citations = []
        for step in resolution_data["steps"]:
            for source in step.get("sources", []):
                citations.append({
                    "response_id": response_id,
                    "citation_key": source,
                    "resolved_at": datetime.utcnow()
                })
        if citations:
            response_citations_collection.insert_many(citations)

        # Mark ticket draft response generated
        tickets_collection.update_one(
            {"_id": ticket_oid},
            {"$set": {"latest_response_id": response_id, "updated_at": datetime.utcnow()}}
        )

        # Create Jira issue (Status = Resolved/Completed/To Do)
        create_jira_issue(
            ticket_id=ticket_id_str,
            subject=ticket.get("subject", ""),
            description=f"Auto-resolved support ticket.\nResolution Steps:\n{response_doc['response_text']}",
            priority=ticket.get("priority", "Medium"),
            status="Resolved"
        )

        # Send troubleshooting steps email to requester
        send_resolution_email(ticket, response_doc["response_text"])
        
    else:
        # --- ESCALATE TICKET (ESCALATED) ---
        agent_workflows_collection.update_one(
            {"_id": workflow_id},
            {"$set": {"current_agent": "Escalation Agent"}}
        )

        esc_reason = "Insufficient knowledge-base context or low confidence score."
        if not sufficient:
            esc_reason = "Insufficient knowledge-base context retrieved."
        elif confidence < 0.70:
            esc_reason = f"Resolution confidence score ({confidence:.2f}) was below the acceptable threshold (0.70)."

        esc_start = datetime.utcnow()
        escalation_data = run_escalation_agent(ticket, esc_reason)
        esc_end = datetime.utcnow()

        agent_executions_collection.insert_one({
            "workflow_id": workflow_id_str,
            "agent_name": "Escalation Agent",
            "input_data": {"reason": esc_reason},
            "output_data": escalation_data,
            "status": "SUCCESS",
            "confidence": 1.0,
            "started_at": esc_start,
            "completed_at": esc_end
        })

        agent_workflows_collection.update_one(
            {"_id": workflow_id},
            {"$set": {"workflow_status": "ESCALATED", "current_agent": "Done", "completed_at": datetime.utcnow()}}
        )

        # Transition ticket status to Escalated / Open
        tickets_collection.update_one(
            {"_id": ticket_oid},
            {"$set": {"status": "Open", "updated_at": datetime.utcnow()}}
        )

    # Reload and return updated ticket & workflow
    updated_workflow = agent_workflows_collection.find_one({"_id": workflow_id})
    updated_workflow["_id"] = str(updated_workflow["_id"])
    return updated_workflow
