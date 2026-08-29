from datetime import datetime
import urllib.request
import json
from AIticket.db import (
    db,
    users_collection,
    tickets_collection,
    knowledge_articles_collection,
    article_chunks_collection,
    agent_workflows_collection,
    agent_executions_collection,
    jira_tickets_collection,
    email_logs_collection,
    audit_logs_collection,
)

OLLAMA_URL = "http://localhost:11434/api/tags"

def get_system_overview():
    """
    Retrieves system health, collection document counts, vector index state,
    and Ollama model operational status.
    """
    db_status = "HEALTHY"
    try:
        # Ping MongoDB database
        db.command("ping")
    except Exception as e:
        db_status = f"DEGRADED: {e}"

    collections_count = {
        "users": users_collection.count_documents({}),
        "tickets": tickets_collection.count_documents({}),
        "knowledge_articles": knowledge_articles_collection.count_documents({}),
        "article_chunks": article_chunks_collection.count_documents({}),
        "agent_workflows": agent_workflows_collection.count_documents({}),
        "agent_executions": agent_executions_collection.count_documents({}),
        "jira_tickets": jira_tickets_collection.count_documents({}),
        "email_logs": email_logs_collection.count_documents({}),
        "audit_logs": audit_logs_collection.count_documents({}),
    }

    active_workflows = agent_workflows_collection.count_documents({"workflow_status": "RUNNING"})

    # Check Ollama LLM availability
    ollama_status = "UNKNOWN"
    try:
        req = urllib.request.Request(OLLAMA_URL, method="GET")
        with urllib.request.urlopen(req, timeout=3) as res:
            if res.status == 200:
                ollama_status = "ONLINE"
            else:
                ollama_status = f"HTTP_{res.status}"
    except Exception:
        ollama_status = "OFFLINE_OR_FALLBACK_ACTIVE"

    return {
        "status": "OPERATIONAL" if db_status == "HEALTHY" else "DEGRADED",
        "timestamp": datetime.utcnow(),
        "database_status": db_status,
        "collections_count": collections_count,
        "vector_indices_count": 1, # MongoDB Atlas Vector Search index configured
        "active_agent_workflows": active_workflows,
        "ollama_model_status": ollama_status,
    }

def get_system_status():
    """
    Returns quick operational health status for system monitoring.
    """
    return {
        "status": "OPERATIONAL",
        "uptime_status": "UP",
        "version": "3.0.0",
    }
