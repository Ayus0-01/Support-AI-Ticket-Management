from django.urls import path
from apps.history.views import audit_logs_view, ticket_audit_history_view

urlpatterns = [
    path("audit-logs/", audit_logs_view, name="history-audit-logs"),
    path("tickets/<str:ticket_id>/", ticket_audit_history_view, name="history-ticket-audit"),
]
