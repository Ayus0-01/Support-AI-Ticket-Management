from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from bson import ObjectId
from datetime import datetime

from AIticket.db import (
    users_collection,
    tickets_collection,
    agent_workflows_collection,
    agent_executions_collection,
)

from apps.agents.services.orchestrator import (
    start_workflow_orchestration,
    run_diagnosis_agent,
    run_retrieval_agent,
    run_resolution_agent,
    run_escalation_agent,
)
from apps.agents.services.jira_service import (
    create_jira_issue,
    get_jira_mapping,
    update_jira_issue,
    sync_jira_status_to_supportpilot,
)
from apps.agents.services.email_service import (
    send_ticket_created_email,
    send_resolution_email,
    send_escalation_email,
    send_resolved_email,
    get_email_logs,
)

def authenticate_user(request):
    """
    Helper to authenticate requests using manual Bearer JWT parsing.
    Returns (user_doc, None) on success or (None, Response) on error.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None, Response(
            {"message": "Authorization header missing."},
            status=status.HTTP_401_UNAUTHORIZED
        )
    try:
        parts = auth_header.split(" ")
        if len(parts) != 2 or parts[0] != "Bearer":
            return None, Response(
                {"message": "Invalid Authorization header."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        token = parts[1]
        access_token = AccessToken(token)
        user_id = access_token["user_id"]
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return None, Response(
                {"message": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        if user.get("status") == "Inactive":
            return None, Response(
                {"message": "User account is deactivated."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return user, None
    except Exception:
        return None, Response(
            {"message": "Invalid or expired token."},
            status=status.HTTP_401_UNAUTHORIZED
        )

# ==========================================
# 1. Multi-Agent Orchestrator View Handlers
# ==========================================

@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def workflow_start_view(request):
    """
    POST /api/agent/workflow/start
    Body: {"ticket_id": "..."}
    """
    user, err_response = authenticate_user(request)
    if err_response:
        return err_response

    ticket_id = request.data.get("ticket_id")
    if not ticket_id:
        return Response({"message": "ticket_id is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        workflow = start_workflow_orchestration(ticket_id)
        return Response(workflow, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def workflow_status_view(request, ticket_id):
    """
    GET /api/agent/workflow/:ticketId
    """
    user, err_response = authenticate_user(request)
    if err_response:
        return err_response

    workflow = agent_workflows_collection.find_one({"ticket_id": str(ticket_id)})
    if not workflow:
        return Response({"message": "No active workflow found for this ticket."}, status=status.HTTP_404_NOT_FOUND)
    
    workflow["_id"] = str(workflow["_id"])
    return Response(workflow, status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def workflow_agents_view(request, ticket_id):
    """
    GET /api/agent/workflow/:ticketId/agents
    """
    user, err_response = authenticate_user(request)
    if err_response:
        return err_response

    workflow = agent_workflows_collection.find_one({"ticket_id": str(ticket_id)})
    if not workflow:
        return Response({"message": "No active workflow found for this ticket."}, status=status.HTTP_404_NOT_FOUND)
    
    executions = list(agent_executions_collection.find({"workflow_id": str(workflow["_id"])}))
    for exec_doc in executions:
        exec_doc["_id"] = str(exec_doc["_id"])
        
    return Response(executions, status=status.HTTP_200_OK)

@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def agent_diagnosis_view(request):
    """
    POST /api/agent/diagnosis
    """
    user, err_response = authenticate_user(request)
    if err_response:
        return err_response

    ticket_id = request.data.get("ticket_id")
    if not ticket_id:
        return Response({"message": "ticket_id is required."}, status=status.HTTP_400_BAD_REQUEST)

    ticket = tickets_collection.find_one({"_id": ObjectId(ticket_id)})
    if not ticket:
        return Response({"message": "Ticket not found."}, status=status.HTTP_404_NOT_FOUND)

    diagnosis = run_diagnosis_agent(ticket)
    return Response(diagnosis, status=status.HTTP_200_OK)

@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def agent_retrieve_view(request):
    """
    POST /api/agent/retrieve
    """
    user, err_response = authenticate_user(request)
    if err_response:
        return err_response

    ticket_id = request.data.get("ticket_id")
    diagnosis = request.data.get("diagnosis")
    if not ticket_id:
        return Response({"message": "ticket_id is required."}, status=status.HTTP_400_BAD_REQUEST)

    ticket = tickets_collection.find_one({"_id": ObjectId(ticket_id)})
    if not ticket:
        return Response({"message": "Ticket not found."}, status=status.HTTP_404_NOT_FOUND)

    retrieval = run_retrieval_agent(ticket, diagnosis)
    # Simplify response for JSON serialization
    retrieval.pop("results", None)
    return Response(retrieval, status=status.HTTP_200_OK)

@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def agent_resolve_view(request):
    """
    POST /api/agent/resolve
    """
    user, err_response = authenticate_user(request)
    if err_response:
        return err_response

    ticket_id = request.data.get("ticket_id")
    diagnosis = request.data.get("diagnosis", {})
    retrieval = request.data.get("retrieval", {})
    
    if not ticket_id:
        return Response({"message": "ticket_id is required."}, status=status.HTTP_400_BAD_REQUEST)

    ticket = tickets_collection.find_one({"_id": ObjectId(ticket_id)})
    if not ticket:
        return Response({"message": "Ticket not found."}, status=status.HTTP_404_NOT_FOUND)

    resolution = run_resolution_agent(ticket, diagnosis, retrieval)
    return Response(resolution, status=status.HTTP_200_OK)

@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def agent_escalate_view(request):
    """
    POST /api/agent/escalate
    """
    user, err_response = authenticate_user(request)
    if err_response:
        return err_response

    ticket_id = request.data.get("ticket_id")
    reason = request.data.get("reason", "Low resolution confidence.")
    if not ticket_id:
        return Response({"message": "ticket_id is required."}, status=status.HTTP_400_BAD_REQUEST)

    ticket = tickets_collection.find_one({"_id": ObjectId(ticket_id)})
    if not ticket:
        return Response({"message": "Ticket not found."}, status=status.HTTP_404_NOT_FOUND)

    escalation = run_escalation_agent(ticket, reason)
    return Response(escalation, status=status.HTTP_200_OK)

# ==========================================
# 2. Jira Integration View Handlers
# ==========================================

@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def jira_create_view(request):
    """
    POST /api/jira/tickets
    Body: {"ticket_id": "..."}
    """
    user, err_response = authenticate_user(request)
    if err_response:
        return err_response

    ticket_id = request.data.get("ticket_id")
    if not ticket_id:
        return Response({"message": "ticket_id is required."}, status=status.HTTP_400_BAD_REQUEST)

    ticket = tickets_collection.find_one({"_id": ObjectId(ticket_id)})
    if not ticket:
        return Response({"message": "Ticket not found."}, status=status.HTTP_404_NOT_FOUND)

    mapping = create_jira_issue(
        ticket_id=str(ticket_id),
        subject=ticket.get("subject", ""),
        description=ticket.get("description", ""),
        priority=ticket.get("priority", "Medium"),
        status=ticket.get("status", "Open")
    )
    mapping["_id"] = str(mapping["_id"])
    return Response(mapping, status=status.HTTP_201_CREATED)

@api_view(["GET", "PUT"])
@authentication_classes([])
@permission_classes([AllowAny])
def jira_detail_or_update_view(request, ticket_id):
    """
    GET or PUT /api/jira/tickets/:ticketId
    """
    user, err_response = authenticate_user(request)
    if err_response:
        return err_response

    if request.method == "GET":
        mapping = get_jira_mapping(ticket_id)
        if not mapping:
            return Response({"message": "No Jira ticket mapping found for this ticket."}, status=status.HTTP_404_NOT_FOUND)
        mapping["_id"] = str(mapping["_id"])
        return Response(mapping, status=status.HTTP_200_OK)

    elif request.method == "PUT":
        mapping = update_jira_issue(ticket_id, request.data)
        if not mapping:
            return Response({"message": "No Jira ticket mapping found."}, status=status.HTTP_404_NOT_FOUND)
        mapping["_id"] = str(mapping["_id"])
        return Response(mapping, status=status.HTTP_200_OK)

@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def jira_sync_view(request):
    """
    POST /api/jira/sync
    """
    user, err_response = authenticate_user(request)
    if err_response:
        return err_response

    count = sync_jira_status_to_supportpilot()
    return Response({"message": "Jira synchronization complete.", "updated_tickets_count": count}, status=status.HTTP_200_OK)

# ==========================================
# 3. Email Automation View Handlers
# ==========================================

@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def email_created_view(request):
    """
    POST /api/email/ticket-created
    """
    user, err_response = authenticate_user(request)
    if err_response:
        return err_response

    ticket_id = request.data.get("ticket_id")
    if not ticket_id:
        return Response({"message": "ticket_id is required."}, status=status.HTTP_400_BAD_REQUEST)

    ticket = tickets_collection.find_one({"_id": ObjectId(ticket_id)})
    if not ticket:
        return Response({"message": "Ticket not found."}, status=status.HTTP_404_NOT_FOUND)

    log_entry = send_ticket_created_email(ticket)
    return Response(log_entry, status=status.HTTP_200_OK)

@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def email_resolution_view(request):
    """
    POST /api/email/resolution
    """
    user, err_response = authenticate_user(request)
    if err_response:
        return err_response

    ticket_id = request.data.get("ticket_id")
    resolution_text = request.data.get("resolution_text")
    if not ticket_id or not resolution_text:
        return Response({"message": "ticket_id and resolution_text are required."}, status=status.HTTP_400_BAD_REQUEST)

    ticket = tickets_collection.find_one({"_id": ObjectId(ticket_id)})
    if not ticket:
        return Response({"message": "Ticket not found."}, status=status.HTTP_404_NOT_FOUND)

    log_entry = send_resolution_email(ticket, resolution_text)
    return Response(log_entry, status=status.HTTP_200_OK)

@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def email_escalation_view(request):
    """
    POST /api/email/escalation
    """
    user, err_response = authenticate_user(request)
    if err_response:
        return err_response

    ticket_id = request.data.get("ticket_id")
    reason = request.data.get("reason", "Low confidence score.")
    if not ticket_id:
        return Response({"message": "ticket_id is required."}, status=status.HTTP_400_BAD_REQUEST)

    ticket = tickets_collection.find_one({"_id": ObjectId(ticket_id)})
    if not ticket:
        return Response({"message": "Ticket not found."}, status=status.HTTP_404_NOT_FOUND)

    log_entry = send_escalation_email(ticket, reason)
    return Response(log_entry, status=status.HTTP_200_OK)

@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def email_resolved_view(request):
    """
    POST /api/email/resolved
    """
    user, err_response = authenticate_user(request)
    if err_response:
        return err_response

    ticket_id = request.data.get("ticket_id")
    if not ticket_id:
        return Response({"message": "ticket_id is required."}, status=status.HTTP_400_BAD_REQUEST)

    ticket = tickets_collection.find_one({"_id": ObjectId(ticket_id)})
    if not ticket:
        return Response({"message": "Ticket not found."}, status=status.HTTP_404_NOT_FOUND)

    log_entry = send_resolved_email(ticket)
    return Response(log_entry, status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def email_logs_view(request, ticket_id):
    """
    GET /api/email/logs/:ticketId
    """
    user, err_response = authenticate_user(request)
    if err_response:
        return err_response

    logs = get_email_logs(ticket_id)
    return Response(logs, status=status.HTTP_200_OK)
