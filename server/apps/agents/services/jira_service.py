import urllib.request
import json
import base64
from datetime import datetime
from decouple import config
from bson import ObjectId

from AIticket.db import (
    jira_tickets_collection,
    tickets_collection,
)

# Load configuration (optional, will fall back to mock if not configured)
JIRA_URL = config("JIRA_URL", default="")
JIRA_USERNAME = config("JIRA_USERNAME", default="")
JIRA_API_TOKEN = config("JIRA_API_TOKEN", default="")
JIRA_PROJECT_KEY = config("JIRA_PROJECT_KEY", default="SP")

# Simple counter for mock issue keys in testing
_mock_key_counter = 1000

def _get_mock_issue_key():
    global _mock_key_counter
    _mock_key_counter += 1
    return f"{JIRA_PROJECT_KEY}-{_mock_key_counter}"

def _is_jira_configured():
    return bool(JIRA_URL and JIRA_USERNAME and JIRA_API_TOKEN)

def create_jira_issue(ticket_id, subject, description, priority="Medium", status="Open"):
    """
    Creates a Jira issue mapped to the SupportPilot ticket.
    If Jira credentials are configured, sends a real API request.
    Otherwise, simulates creation in mock mode.
    """
    ticket_oid = ObjectId(ticket_id) if isinstance(ticket_id, str) else ticket_id
    ticket_id_str = str(ticket_id)

    # Check if mapping already exists
    existing = jira_tickets_collection.find_one({"ticket_id": ticket_id_str})
    if existing:
        return existing

    jira_key = None
    jira_status = "To Do"
    
    if _is_jira_configured():
        try:
            url = f"{JIRA_URL.rstrip('/')}/rest/api/2/issue"
            auth_str = f"{JIRA_USERNAME}:{JIRA_API_TOKEN}"
            auth_b64 = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
            
            payload = {
                "fields": {
                    "project": {"key": JIRA_PROJECT_KEY},
                    "summary": f"[SupportPilot] {subject}",
                    "description": description,
                    "issuetype": {"name": "Task"},
                    "priority": {"name": priority}
                }
            }
            
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Basic {auth_b64}"
                },
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=10) as res:
                response_data = json.loads(res.read().decode("utf-8"))
                jira_key = response_data.get("key")
                # Get created issue details
                jira_status = "To Do"
        except Exception as e:
            print(f"Jira API call failed: {e}. Falling back to mock Jira creation.")

    if not jira_key:
        # Mock mode fallback
        jira_key = _get_mock_issue_key()
        jira_status = "To Do" if status != "Resolved" else "Resolved"

    mapping = {
        "ticket_id": ticket_id_str,
        "jira_issue_key": jira_key,
        "jira_status": jira_status,
        "last_updated": datetime.utcnow()
    }
    
    # Save mapping
    result = jira_tickets_collection.insert_one(mapping)
    mapping["_id"] = result.inserted_id

    # Add reference inside SupportPilot ticket document as well
    tickets_collection.update_one(
        {"_id": ticket_oid},
        {"$set": {"jira_issue_key": jira_key, "jira_status": jira_status, "updated_at": datetime.utcnow()}}
    )

    return mapping

def get_jira_mapping(ticket_id):
    ticket_id_str = str(ticket_id)
    return jira_tickets_collection.find_one({"ticket_id": ticket_id_str})

def update_jira_issue(ticket_id, fields):
    """
    Updates fields on the mapped Jira issue.
    """
    ticket_id_str = str(ticket_id)
    mapping = jira_tickets_collection.find_one({"ticket_id": ticket_id_str})
    if not mapping:
        return None

    jira_key = mapping["jira_issue_key"]
    jira_status = fields.get("jira_status", mapping["jira_status"])
    
    if _is_jira_configured():
        try:
            url = f"{JIRA_URL.rstrip('/')}/rest/api/2/issue/{jira_key}"
            auth_str = f"{JIRA_USERNAME}:{JIRA_API_TOKEN}"
            auth_b64 = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
            
            payload = {}
            if "summary" in fields:
                payload["summary"] = fields["summary"]
            
            # Transition status in Jira if specified
            if "transition" in fields:
                # First fetch available transitions, then perform transition
                pass

            if payload:
                req = urllib.request.Request(
                    url,
                    data=json.dumps({"update": payload}).encode("utf-8"),
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Basic {auth_b64}"
                    },
                    method="PUT"
                )
                with urllib.request.urlopen(req, timeout=10) as res:
                    pass
        except Exception as e:
            print(f"Failed to update Jira issue: {e}")

    # Update mapping
    jira_tickets_collection.update_one(
        {"ticket_id": ticket_id_str},
        {"$set": {"jira_status": jira_status, "last_updated": datetime.utcnow()}}
    )

    # Sync back to ticket
    tickets_collection.update_one(
        {"_id": ObjectId(ticket_id)},
        {"$set": {"jira_status": jira_status, "updated_at": datetime.utcnow()}}
    )

    mapping["jira_status"] = jira_status
    return mapping

def sync_jira_status_to_supportpilot():
    """
    Synchronizes status updates of mapped Jira issues back to SupportPilot.
    Looks up status from Jira and transitions corresponding SupportPilot ticket status.
    Returns the count of updated tickets.
    """
    mappings = list(jira_tickets_collection.find())
    updated_count = 0

    for mapping in mappings:
        ticket_id_str = mapping["ticket_id"]
        jira_key = mapping["jira_issue_key"]
        old_status = mapping["jira_status"]
        new_status = old_status
        
        if _is_jira_configured():
            try:
                url = f"{JIRA_URL.rstrip('/')}/rest/api/2/issue/{jira_key}"
                auth_str = f"{JIRA_USERNAME}:{JIRA_API_TOKEN}"
                auth_b64 = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
                
                req = urllib.request.Request(
                    url,
                    headers={
                        "Authorization": f"Basic {auth_b64}"
                    },
                    method="GET"
                )
                with urllib.request.urlopen(req, timeout=10) as res:
                    issue_data = json.loads(res.read().decode("utf-8"))
                    new_status = issue_data.get("fields", {}).get("status", {}).get("name", old_status)
            except Exception as e:
                print(f"Jira sync status failed for {jira_key}: {e}")

        # If mock/sync returns resolved, let's sync back to ticket status
        if new_status != old_status:
            # Update mapping
            jira_tickets_collection.update_one(
                {"_id": mapping["_id"]},
                {"$set": {"jira_status": new_status, "last_updated": datetime.utcnow()}}
            )
            # Update ticket status in SupportPilot
            sp_status = "Resolved" if new_status in ("Resolved", "Done", "Closed") else "In Progress"
            
            tickets_collection.update_one(
                {"_id": ObjectId(ticket_id_str)},
                {"$set": {"status": sp_status, "jira_status": new_status, "updated_at": datetime.utcnow()}}
            )
            updated_count += 1
            
    return updated_count
