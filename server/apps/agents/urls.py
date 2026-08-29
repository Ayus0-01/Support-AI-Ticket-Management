from django.urls import path
from .views import (
    workflow_start_view,
    workflow_status_view,
    workflow_agents_view,
    agent_diagnosis_view,
    agent_retrieve_view,
    agent_resolve_view,
    agent_escalate_view,
)

urlpatterns = [
    path("workflow/start", workflow_start_view, name="workflow-start"),
    path("workflow/<str:ticket_id>/", workflow_status_view, name="workflow-status"),
    path("workflow/<str:ticket_id>/agents/", workflow_agents_view, name="workflow-agents"),
    path("diagnosis", agent_diagnosis_view, name="agent-diagnosis"),
    path("retrieve", agent_retrieve_view, name="agent-retrieve"),
    path("resolve", agent_resolve_view, name="agent-resolve"),
    path("escalate", agent_escalate_view, name="agent-escalate"),
]
