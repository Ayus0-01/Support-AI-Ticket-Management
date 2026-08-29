from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from apps.agents.views import authenticate_user
from apps.history.services import get_audit_logs, get_ticket_audit_history

@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def audit_logs_view(request):
    """
    GET /api/history/audit-logs/
    Admin endpoint for viewing global audit logs.
    """
    user, err_response = authenticate_user(request)
    if err_response:
        return err_response

    if user.get("role") != "Admin":
        return Response({"message": "Admin access required."}, status=status.HTTP_403_FORBIDDEN)

    action_type = request.query_params.get("action_type")
    target_type = request.query_params.get("target_type")
    limit = int(request.query_params.get("limit", 50))

    logs = get_audit_logs(action_type=action_type, target_type=target_type, limit=limit)
    return Response(logs, status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def ticket_audit_history_view(request, ticket_id):
    """
    GET /api/history/tickets/<ticket_id>/
    Returns aggregated audit trail and event history for a given ticket.
    """
    user, err_response = authenticate_user(request)
    if err_response:
        return err_response

    history_data = get_ticket_audit_history(ticket_id)
    if not history_data:
        return Response({"message": "Ticket not found."}, status=status.HTTP_404_NOT_FOUND)

    return Response(history_data, status=status.HTTP_200_OK)
