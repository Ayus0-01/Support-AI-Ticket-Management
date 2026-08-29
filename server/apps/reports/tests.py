from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status
from unittest.mock import patch, MagicMock
from bson import ObjectId
from datetime import datetime

from apps.reports import views

class ReportsAppTests(SimpleTestCase):
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

    @patch("apps.reports.views.authenticate_user")
    @patch("apps.reports.services.tickets_collection")
    @patch("apps.reports.services.agent_workflows_collection")
    @patch("apps.reports.services.resolution_feedback_collection")
    def test_analytics_summary_view_admin_success(self, mock_feedback, mock_workflows, mock_tickets, mock_auth):
        mock_auth.return_value = (self.mock_admin, None)

        mock_tickets.find.return_value = [
            {"_id": ObjectId(), "status": "Resolved", "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()},
            {"_id": ObjectId(), "status": "Open", "created_at": datetime.utcnow()}
        ]
        mock_workflows.find.return_value = [
            {"workflow_status": "COMPLETED", "final_confidence": 0.85}
        ]
        mock_feedback.find.return_value = [
            {"rating": 5}
        ]

        request = self.factory.get("/api/reports/analytics/", HTTP_AUTHORIZATION="Bearer token")
        response = views.analytics_summary_view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_tickets"], 2)
        self.assertEqual(response.data["ai_resolved_count"], 1)

    @patch("apps.reports.views.authenticate_user")
    def test_analytics_summary_view_user_forbidden(self, mock_auth):
        mock_auth.return_value = (self.mock_user, None)
        request = self.factory.get("/api/reports/analytics/", HTTP_AUTHORIZATION="Bearer token")
        response = views.analytics_summary_view(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch("apps.reports.views.authenticate_user")
    @patch("apps.reports.services.tickets_collection")
    def test_sla_metrics_view_success(self, mock_tickets, mock_auth):
        mock_auth.return_value = (self.mock_admin, None)
        mock_tickets.find.return_value = [
            {"_id": ObjectId(), "status": "Resolved", "priority": "P1", "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()}
        ]

        request = self.factory.get("/api/reports/sla/", HTTP_AUTHORIZATION="Bearer token")
        response = views.sla_metrics_view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_evaluated_tickets"], 1)
        self.assertEqual(response.data["overall_compliance_rate"], 100.0)

    @patch("apps.reports.views.authenticate_user")
    @patch("apps.reports.services.agent_executions_collection")
    @patch("apps.reports.services.agent_workflows_collection")
    def test_agent_performance_view_success(self, mock_workflows, mock_execs, mock_auth):
        mock_auth.return_value = (self.mock_admin, None)
        mock_execs.find.return_value = [
            {"agent_name": "Diagnosis Agent", "started_at": datetime.utcnow(), "completed_at": datetime.utcnow()}
        ]
        mock_workflows.find.return_value = [
            {"workflow_status": "COMPLETED"}
        ]

        request = self.factory.get("/api/reports/agent-performance/", HTTP_AUTHORIZATION="Bearer token")
        response = views.agent_performance_view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_agent_executions"], 1)
