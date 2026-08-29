from django.urls import path
from apps.reports.views import (
    analytics_summary_view,
    sla_metrics_view,
    agent_performance_view,
)

urlpatterns = [
    path("analytics/", analytics_summary_view, name="reports-analytics"),
    path("sla/", sla_metrics_view, name="reports-sla"),
    path("agent-performance/", agent_performance_view, name="reports-agent-performance"),
]
