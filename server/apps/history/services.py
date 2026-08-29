from datetime import datetime
from bson import ObjectId
from AIticket.db import (
    audit_logs_collection,
    tickets_collection,
    status_history_collection,
    comments_collection,
    agent_workflows_collection,
    agent_executions_collection,
    ticket_responses_collection,
    email_logs_collection,
    jira_tickets_collection,
    resolution_feedback_collection,
)

def log_audit_event(user_id=None, username=None, action_type="SYSTEM_ACTION", target_type="GENERAL", target_id=None, details=None, ip_address=None):
    """
    Persists an immutable audit log entry.
    """
    log_doc = {
        "user_id": str(user_id) if user_id else None,
        "username": username or "System",
        "action_type": action_type,
        "target_type": target_type,
        "target_id": str(target_id) if target_id else None,
        "details": details or {},
        "ip_address": ip_address,
        "timestamp": datetime.utcnow()
    }
    res = audit_logs_collection.insert_one(log_doc)
    log_doc["_id"] = str(res.inserted_id)
    return log_doc

def get_audit_logs(action_type=None, target_type=None, limit=50):
    """
    Queries audit logs for compliance monitoring.
    """
    query = {}
    if action_type:
        query["action_type"] = action_type
    if target_type:
        query["target_type"] = target_type

    logs = list(audit_logs_collection.find(query).sort("timestamp", -1).limit(limit))
    for doc in logs:
        doc["_id"] = str(doc["_id"])
    return logs

def get_ticket_audit_history(ticket_id):
    """
    Aggregates full lifecycle audit history for a ticket across multiple collections.
    """
    ticket_id_str = str(ticket_id)
    try:
        ticket_oid = ObjectId(ticket_id_str)
    except Exception:
        ticket_oid = None

    ticket = tickets_collection.find_one({"$or": [{"_id": ticket_oid}, {"ticket_id": ticket_id_str}]})
    if not ticket:
        return None

    actual_oid = ticket["_id"]
    actual_oid_str = str(actual_oid)

    timeline_events = []

    # 1. Ticket Creation Event
    timeline_events.append({
        "event_type": "TICKET_CREATED",
        "timestamp": ticket.get("created_at") or datetime.utcnow(),
        "performed_by": ticket.get("requester", {}).get("username", "Requester"),
        "details": {
            "subject": ticket.get("subject"),
            "category": ticket.get("category"),
            "subcategory": ticket.get("subcategory"),
            "severity": ticket.get("severity"),
            "priority": ticket.get("priority")
        }
    })

    # 2. Status Transitions History
    status_entries = list(status_history_collection.find({"ticket_id": actual_oid}))
    for st in status_entries:
        timeline_events.append({
            "event_type": "STATUS_CHANGED",
            "timestamp": st.get("changed_at") or datetime.utcnow(),
            "performed_by": st.get("changed_by", "System"),
            "details": {
                "old_status": st.get("old_status"),
                "new_status": st.get("new_status"),
                "reason": st.get("reason", "")
            }
        })

    # 3. Comments History
    comments = list(comments_collection.find({"ticket_id": actual_oid}))
    for c in comments:
        timeline_events.append({
            "event_type": "COMMENT_ADDED",
            "timestamp": c.get("created_at") or datetime.utcnow(),
            "performed_by": c.get("author", {}).get("username", "User"),
            "details": {
                "comment_text": c.get("comment_text", ""),
                "is_internal": c.get("is_internal", False)
            }
        })

    # 4. Multi-Agent Workflow Executions
    workflow = agent_workflows_collection.find_one({"ticket_id": actual_oid_str})
    if workflow:
        timeline_events.append({
            "event_type": "AGENT_WORKFLOW_STARTED",
            "timestamp": workflow.get("started_at") or datetime.utcnow(),
            "performed_by": "AI Multi-Agent Orchestrator",
            "details": {
                "workflow_status": workflow.get("workflow_status"),
                "final_confidence": workflow.get("final_confidence")
            }
        })
        execs = list(agent_executions_collection.find({"workflow_id": str(workflow["_id"])}))
        for ex in execs:
            timeline_events.append({
                "event_type": "AGENT_STEP_EXECUTED",
                "timestamp": ex.get("started_at") or datetime.utcnow(),
                "performed_by": ex.get("agent_name", "AI Agent"),
                "details": {
                    "status": ex.get("status"),
                    "confidence": ex.get("confidence"),
                    "output_data": ex.get("output_data", {})
                }
            })

    # 5. Ticket Resolution Responses
    responses = list(ticket_responses_collection.find({"ticket_id": actual_oid}))
    for r in responses:
        timeline_events.append({
            "event_type": "RESOLUTION_GENERATED",
            "timestamp": r.get("created_at") or datetime.utcnow(),
            "performed_by": "Resolution Generation Agent",
            "details": {
                "model": r.get("model"),
                "latency_ms": r.get("latency_ms"),
                "response_id": str(r["_id"])
            }
        })

    # 6. Email Communication Logs
    emails = list(email_logs_collection.find({"ticket_id": actual_oid_str}))
    for em in emails:
        timeline_events.append({
            "event_type": "EMAIL_DISPATCHED",
            "timestamp": em.get("sent_at") or datetime.utcnow(),
            "performed_by": "Email Automation Service",
            "details": {
                "recipient": em.get("recipient"),
                "subject": em.get("subject"),
                "email_type": em.get("email_type"),
                "status": em.get("status")
            }
        })

    # 7. Jira Issue Mappings
    jira_doc = jira_tickets_collection.find_one({"ticket_id": actual_oid_str})
    if jira_doc:
        timeline_events.append({
            "event_type": "JIRA_ISSUE_SYNCED",
            "timestamp": jira_doc.get("last_updated") or datetime.utcnow(),
            "performed_by": "Jira Service Integration",
            "details": {
                "jira_issue_key": jira_doc.get("jira_issue_key"),
                "jira_status": jira_doc.get("jira_status")
            }
        })

    # 8. Resolution Feedback
    feedbacks = list(resolution_feedback_collection.find({"ticket_id": actual_oid}))
    for fb in feedbacks:
        timeline_events.append({
            "event_type": "FEEDBACK_SUBMITTED",
            "timestamp": fb.get("created_at") or datetime.utcnow(),
            "performed_by": fb.get("submitted_by", "User"),
            "details": {
                "rating": fb.get("rating"),
                "reason": fb.get("reason", "")
            }
        })

    # Sort all events chronologically
    timeline_events.sort(key=lambda x: x["timestamp"] if isinstance(x["timestamp"], datetime) else datetime.min)

    return {
        "ticket_id": actual_oid_str,
        "human_readable_id": ticket.get("ticket_id"),
        "subject": ticket.get("subject"),
        "current_status": ticket.get("status"),
        "total_events": len(timeline_events),
        "history": timeline_events
    }
