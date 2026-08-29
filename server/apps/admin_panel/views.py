from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from apps.agents.views import authenticate_user
from apps.admin_panel.services import get_system_overview, get_system_status

@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def admin_overview_view(request):
    """
    GET /api/admin-panel/overview/
    Returns high-level system operations, database document counts, and LLM status.
    Role: Admin.
    """
    user, err_response = authenticate_user(request)
    if err_response:
        return err_response

    if user.get("role") != "Admin":
        return Response({"message": "Admin access required."}, status=status.HTTP_403_FORBIDDEN)

    data = get_system_overview()
    return Response(data, status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def system_status_view(request):
    """
    GET /api/admin-panel/system-status/
    Pings system status. Accessible to authenticated users.
    """
    user, err_response = authenticate_user(request)
    if err_response:
        return err_response

    data = get_system_status()
    return Response(data, status=status.HTTP_200_OK)
