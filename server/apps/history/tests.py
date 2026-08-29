from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status
from unittest.mock import patch, MagicMock
from bson import ObjectId
from datetime import datetime

from apps.history import views

class HistoryAppTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin_id = ObjectId()
        self.user_id = ObjectId()
        self.ticket_id = ObjectId()

        self.mock_admin = {
            "_id": self.admin_id,
            "username": "admin_user",
            "email": "admin@example.com",
            "role": "Admin",
            "status": "Active"
        }

        self.mock_user = {
            "_id": self.user_id,
            "username": "regular_user",
            "email": "user@example.com",
            "role": "User",
            "status": "Active"
        }

    @patch("apps.history.views.authenticate_user")
    @patch("apps.history.services.audit_logs_collection")
    def test_audit_logs_view_admin_success(self, mock_audit_col, mock_auth):
        mock_auth.return_value = (self.mock_admin, None)
        mock_audit_col.find.return_value.sort.return_value.limit.return_value = [
            {
                "_id": ObjectId(),
                "user_id": str(self.admin_id),
                "action_type": "USER_ROLE_UPDATED",
                "target_type": "USER",
                "timestamp": datetime.utcnow()
            }
        ]

        request = self.factory.get("/api/history/audit-logs/", HTTP_AUTHORIZATION="Bearer admin-token")
        response = views.audit_logs_view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    @patch("apps.history.views.authenticate_user")
    def test_audit_logs_view_user_forbidden(self, mock_auth):
        mock_auth.return_value = (self.mock_user, None)

        request = self.factory.get("/api/history/audit-logs/", HTTP_AUTHORIZATION="Bearer user-token")
        response = views.audit_logs_view(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch("apps.history.views.authenticate_user")
    @patch("apps.history.services.tickets_collection")
    @patch("apps.history.services.status_history_collection")
    @patch("apps.history.services.comments_collection")
    @patch("apps.history.services.agent_workflows_collection")
    @patch("apps.history.services.ticket_responses_collection")
    @patch("apps.history.services.email_logs_collection")
    @patch("apps.history.services.jira_tickets_collection")
    @patch("apps.history.services.resolution_feedback_collection")
    def test_ticket_audit_history_view_success(
        self, mock_fb, mock_jira, mock_email, mock_resp, mock_wf, mock_comments, mock_status, mock_tickets, mock_auth
    ):
        mock_auth.return_value = (self.mock_user, None)
        mock_tickets.find_one.return_value = {
            "_id": self.ticket_id,
            "ticket_id": "TCK-101",
            "subject": "VPN Failure",
            "status": "Open",
            "created_at": datetime.utcnow()
        }
        mock_status.find.return_value = []
        mock_comments.find.return_value = []
        mock_wf.find_one.return_value = None
        mock_resp.find.return_value = []
        mock_email.find.return_value = []
        mock_jira.find_one.return_value = None
        mock_fb.find.return_value = []

        request = self.factory.get(f"/api/history/tickets/{self.ticket_id}/", HTTP_AUTHORIZATION="Bearer user-token")
        response = views.ticket_audit_history_view(request, ticket_id=str(self.ticket_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["human_readable_id"], "TCK-101")
        self.assertGreaterEqual(response.data["total_events"], 1)
