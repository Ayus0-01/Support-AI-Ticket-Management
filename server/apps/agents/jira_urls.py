from django.urls import path
from .views import (
    jira_create_view,
    jira_detail_or_update_view,
    jira_sync_view,
)

urlpatterns = [
    path("tickets", jira_create_view, name="jira-create"),
    path("tickets/<str:ticket_id>", jira_detail_or_update_view, name="jira-detail-or-update"),
    path("sync", jira_sync_view, name="jira-sync"),
]
