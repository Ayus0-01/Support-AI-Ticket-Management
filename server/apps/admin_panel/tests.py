from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status
from unittest.mock import patch, MagicMock
from bson import ObjectId

from apps.admin_panel import views

class AdminPanelAppTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin_id = ObjectId()
        self.user_id = ObjectId()

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

    @patch("apps.admin_panel.views.authenticate_user")
    @patch("apps.admin_panel.services.db")
    @patch("apps.admin_panel.services.users_collection")
    @patch("apps.admin_panel.services.tickets_collection")
    @patch("apps.admin_panel.services.agent_workflows_collection")
    def test_admin_overview_view_success(self, mock_wf, mock_tickets, mock_users, mock_db, mock_auth):
        mock_auth.return_value = (self.mock_admin, None)
        mock_db.command.return_value = {"ok": 1}
        mock_users.count_documents.return_value = 5
        mock_tickets.count_documents.return_value = 10
        mock_wf.count_documents.return_value = 2

        request = self.factory.get("/api/admin-panel/overview/", HTTP_AUTHORIZATION="Bearer admin-token")
        response = views.admin_overview_view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "OPERATIONAL")
        self.assertIn("collections_count", response.data)

    @patch("apps.admin_panel.views.authenticate_user")
    def test_admin_overview_view_user_forbidden(self, mock_auth):
        mock_auth.return_value = (self.mock_user, None)

        request = self.factory.get("/api/admin-panel/overview/", HTTP_AUTHORIZATION="Bearer user-token")
        response = views.admin_overview_view(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch("apps.admin_panel.views.authenticate_user")
    def test_system_status_view_success(self, mock_auth):
        mock_auth.return_value = (self.mock_user, None)

        request = self.factory.get("/api/admin-panel/system-status/", HTTP_AUTHORIZATION="Bearer user-token")
        response = views.system_status_view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "OPERATIONAL")
        self.assertEqual(response.data["uptime_status"], "UP")
