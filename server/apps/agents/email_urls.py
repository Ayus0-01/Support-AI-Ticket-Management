from django.urls import path
from .views import (
    email_created_view,
    email_resolution_view,
    email_escalation_view,
    email_resolved_view,
    email_logs_view,
)

urlpatterns = [
    path("ticket-created", email_created_view, name="email-ticket-created"),
    path("resolution", email_resolution_view, name="email-resolution"),
    path("escalation", email_escalation_view, name="email-escalation"),
    path("resolved", email_resolved_view, name="email-resolved"),
    path("logs/<str:ticket_id>", email_logs_view, name="email-logs"),
]
