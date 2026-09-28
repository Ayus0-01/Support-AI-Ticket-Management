"""
API Views for M3 Multi-Agent Engine.
Exposes minimal authenticated endpoints for workflow execution, status, and activity logs.
"""
from typing import Dict, Any, Optional
from bson import ObjectId

from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken

from AIticket.db import users_collection, tickets_collection
from .orchestrator import (
    execute_orchestration_pipeline,
    get_workflow_by_ticket,
    get_workflow_executions,
    get_activity_logs,
)

M3_READ_ROLES = {"Agent", "Support Manager", "Admin"}
M3_EXECUTION_ROLES = {"Agent", "Support Manager", "Admin"}


def _sanitize_object_ids(data: Any) -> Any:
    """
    Recursively converts MongoDB ObjectId instances in dicts, lists, or primitive values
    into JSON-safe strings.
    """
    if isinstance(data, ObjectId):
        return str(data)
    elif isinstance(data, dict):
        return {key: _sanitize_object_ids(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_sanitize_object_ids(item) for item in data]
    elif isinstance(data, tuple):
        return tuple(_sanitize_object_ids(item) for item in data)
    return data


def _redact_resolution_for_support_manager(workflow: Dict[str, Any], executions: list):
    """Expose a read-only resolution summary and evidence, not execution internals."""
    safe_workflow = dict(workflow)
    resolution = safe_workflow.get("resolution")
    if isinstance(resolution, dict):
        safe_workflow["resolution"] = {
            key: resolution[key]
            for key in (
                "summary",
                "troubleshooting_steps",
                "confidence",
            )
            if key in resolution
        }
    else:
        safe_workflow["resolution"] = None

    safe_executions = []
    for execution in executions:
        safe_execution = dict(execution)
        agent_name = safe_execution.get("agent_name")
        if agent_name == "ResolutionAgent":
            safe_execution.pop("output_data", None)

        input_data = safe_execution.get("input_data")
        if agent_name in {"ValidationAgent", "EscalationAgent"} and isinstance(input_data, dict):
            safe_input_data = dict(input_data)
            safe_input_data.pop("resolution", None)
            safe_execution["input_data"] = safe_input_data
        safe_executions.append(safe_execution)

    return safe_workflow, safe_executions


def _authenticate_request(request):
    """
    Validates JWT Bearer token from request headers.
    Returns (user_doc, None) on success, or (None, Response) on error.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None, Response(
            {"message": "Authorization header missing."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    parts = auth_header.split(" ")
    if len(parts) != 2 or parts[0] != "Bearer":
        return None, Response(
            {"message": "Invalid Authorization header."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    token = parts[1]
    try:
        access_token = AccessToken(token)
        user_id = access_token.get("user_id") if isinstance(access_token, dict) else access_token["user_id"]
    except Exception:
        return None, Response(
            {"message": "Invalid or expired token."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None, Response(
            {"message": "Invalid user ID."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user:
        return None, Response(
            {"message": "User not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    return user, None


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def execute_m3_workflow_view(request, ticket_id: Optional[str] = None):
    """
    Triggers execution of the M3 Multi-Agent Orchestration Pipeline for a ticket.
    Requires authentication. Accepts ticket_id via path parameter or request body.
    """
    user, error_response = _authenticate_request(request)
    if error_response:
        return error_response
    if user.get("role", "User") not in M3_EXECUTION_ROLES:
        return Response(
            {"message": "You do not have permission to run the AI workflow."},
            status=status.HTTP_403_FORBIDDEN,
        )

    target_ticket_id = (ticket_id or (request.data.get("ticket_id") if isinstance(request.data, dict) else None) or "").strip()
    if not target_ticket_id:
        return Response(
            {"message": "ticket_id is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    ticket = tickets_collection.find_one({"ticket_id": target_ticket_id})
    if not ticket:
        return Response(
            {"message": f"Ticket '{target_ticket_id}' not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        workflow_result = execute_orchestration_pipeline(
            ticket_id=target_ticket_id,
            ticket_data=ticket,
            # Confidence is diagnostic only; the validation agent still checks
            # that the resolution is grounded and has no blocking limitations.
            confidence_threshold=0.0,
        )
        return Response(
            _sanitize_object_ids({
                "status": "SUCCESS",
                "workflow": workflow_result,
            }),
            status=status.HTTP_200_OK
        )
    except Exception as exc:
        return Response(
            {
                "status": "FAILED",
                "message": str(exc),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def get_m3_workflow_status_view(request, ticket_id: str):
    """
    Retrieves the latest M3 workflow state and step execution logs for a ticket.
    Requires authentication.
    """
    user, error_response = _authenticate_request(request)
    if error_response:
        return error_response
    if user.get("role", "User") not in M3_READ_ROLES:
        return Response(
            {"message": "Staff access is required to view AI workflow details."},
            status=status.HTTP_403_FORBIDDEN,
        )

    target_ticket_id = ticket_id.strip()
    ticket = tickets_collection.find_one({"ticket_id": target_ticket_id})
    if not ticket:
        return Response(
            {"message": f"Ticket '{target_ticket_id}' not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    workflow = get_workflow_by_ticket(target_ticket_id)
    if not workflow:
        return Response(
            {"message": f"No M3 workflow found for ticket '{target_ticket_id}'."},
            status=status.HTTP_404_NOT_FOUND
        )

    workflow_id = workflow.get("workflow_id")
    executions = get_workflow_executions(workflow_id) if workflow_id else []

    if user.get("role") == "Support Manager":
        workflow, executions = _redact_resolution_for_support_manager(workflow, executions)

    return Response(
        _sanitize_object_ids({
            "status": "SUCCESS",
            "workflow": workflow,
            "executions": executions,
        }),
        status=status.HTTP_200_OK
    )


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def get_m3_activity_logs_view(request, ticket_id: Optional[str] = None, workflow_id: Optional[str] = None):
    """
    Retrieves structured activity log entries for a ticket or workflow.
    Requires authentication.
    """
    user, error_response = _authenticate_request(request)
    if error_response:
        return error_response
    if user.get("role", "User") not in M3_READ_ROLES:
        return Response(
            {"message": "Staff access is required to view AI workflow details."},
            status=status.HTTP_403_FORBIDDEN,
        )

    target_ticket_id = (ticket_id or request.query_params.get("ticket_id") or "").strip()
    target_workflow_id = (workflow_id or request.query_params.get("workflow_id") or "").strip()

    if not target_ticket_id and not target_workflow_id:
        return Response(
            {"message": "Either ticket_id or workflow_id is required to fetch activity logs."},
            status=status.HTTP_400_BAD_REQUEST
        )

    logs = get_activity_logs(
        ticket_id=target_ticket_id if target_ticket_id else None,
        workflow_id=target_workflow_id if target_workflow_id else None,
    )

    return Response(
        _sanitize_object_ids({
            "status": "SUCCESS",
            "activity_logs": logs,
            "count": len(logs),
        }),
        status=status.HTTP_200_OK
    )
