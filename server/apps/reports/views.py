from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from apps.agents.views import authenticate_user
from apps.reports.services import (
    get_analytics_summary,
    get_sla_metrics,
    get_agent_performance_metrics,
)

@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def analytics_summary_view(request):
    """
    GET /api/reports/analytics/
    Returns high-level system analytics: ticket volume, AI resolution rates, latency, CSAT.
    Role: Admin, Agent.
    """
    user, err_response = authenticate_user(request)
    if err_response:
        return err_response

    if user.get("role") not in ("Admin", "Agent"):
        return Response({"message": "Admin or Agent permission required."}, status=status.HTTP_403_FORBIDDEN)

    data = get_analytics_summary()
    return Response(data, status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def sla_metrics_view(request):
    """
    GET /api/reports/sla/
    Returns SLA compliance metrics per priority level.
    Role: Admin, Agent.
    """
    user, err_response = authenticate_user(request)
    if err_response:
        return err_response

    if user.get("role") not in ("Admin", "Agent"):
        return Response({"message": "Admin or Agent permission required."}, status=status.HTTP_403_FORBIDDEN)

    data = get_sla_metrics()
    return Response(data, status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def agent_performance_view(request):
    """
    GET /api/reports/agent-performance/
    Returns AI multi-agent performance and step latency metrics.
    Role: Admin.
    """
    user, err_response = authenticate_user(request)
    if err_response:
        return err_response

    if user.get("role") != "Admin":
        return Response({"message": "Admin access required."}, status=status.HTTP_403_FORBIDDEN)

    data = get_agent_performance_metrics()
    return Response(data, status=status.HTTP_200_OK)
