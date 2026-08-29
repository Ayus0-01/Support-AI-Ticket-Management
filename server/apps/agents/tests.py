from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory
from unittest.mock import patch, MagicMock
from bson import ObjectId
from datetime import datetime

from AIticket.db import (
    users_collection,
    tickets_collection,
    agent_workflows_collection,
    agent_executions_collection,
    jira_tickets_collection,
    email_logs_collection,
    ticket_responses_collection,
)

from apps.agents import views
from apps.agents.services.orchestrator import start_workflow_orchestration
from apps.agents.services import jira_service
from apps.agents.services import email_service

class AgentMilestone3Tests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin_id = ObjectId()
        self.ticket_id = ObjectId()
        
        # Test mock user
        self.mock_user = {
            "_id": self.admin_id,
            "username": "testadmin",
            "email": "admin@example.com",
            "role": "Admin",
            "status": "Active"
        }
        
        # Test mock ticket
        self.mock_ticket = {
            "_id": self.ticket_id,
            "ticket_id": "TCK-100",
            "subject": "VPN connection failure",
            "description": "I cannot connect to the corporate VPN",
            "category": "Network",
            "subcategory": "VPN Access",
            "severity": "High",
            "priority": "P1",
            "status": "Open",
            "requester": {"email": "client@example.com", "username": "John Client"}
        }

    @patch("apps.agents.views.AccessToken")
    @patch("apps.agents.views.users_collection")
    @patch("apps.agents.views.tickets_collection")
    @patch("apps.agents.views.start_workflow_orchestration")
    def test_workflow_start_success(self, mock_orchestrate, mock_tickets, mock_users, mock_access_token):
        mock_access_token.return_value = {"user_id": str(self.admin_id)}
        mock_users.find_one.return_value = self.mock_user
        
        mock_orchestrate.return_value = {
            "ticket_id": str(self.ticket_id),
            "workflow_status": "COMPLETED",
            "current_agent": "Done",
            "final_confidence": 0.85
        }

        request = self.factory.post(
            "/api/agent/workflow/start",
            {"ticket_id": str(self.ticket_id)},
            format="json",
            HTTP_AUTHORIZATION="Bearer valid-token"
        )
        response = views.workflow_start_view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["workflow_status"], "COMPLETED")

    @patch("apps.agents.views.AccessToken")
    @patch("apps.agents.views.users_collection")
    @patch("apps.agents.views.agent_workflows_collection")
    def test_workflow_status_view(self, mock_workflows, mock_users, mock_access_token):
        mock_access_token.return_value = {"user_id": str(self.admin_id)}
        mock_users.find_one.return_value = self.mock_user
        
        mock_workflows.find_one.return_value = {
            "_id": ObjectId(),
            "ticket_id": str(self.ticket_id),
            "workflow_status": "RUNNING",
            "current_agent": "Resolution Agent"
        }

        request = self.factory.get(
            f"/api/agent/workflow/{self.ticket_id}/",
            HTTP_AUTHORIZATION="Bearer valid-token"
        )
        response = views.workflow_status_view(request, ticket_id=str(self.ticket_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["workflow_status"], "RUNNING")
        self.assertEqual(response.data["current_agent"], "Resolution Agent")

    @patch("apps.agents.views.AccessToken")
    @patch("apps.agents.views.users_collection")
    @patch("apps.agents.views.tickets_collection")
    @patch("apps.agents.views.run_diagnosis_agent")
    def test_agent_diagnosis_view(self, mock_run_diag, mock_tickets, mock_users, mock_access_token):
        mock_access_token.return_value = {"user_id": str(self.admin_id)}
        mock_users.find_one.return_value = self.mock_user
        mock_tickets.find_one.return_value = self.mock_ticket
        
        mock_run_diag.return_value = {
            "affected_system": "VPN Service",
            "likely_causes": ["Incorrect connection profile"],
            "missing_information": [],
            "diagnosis_confidence": 0.85
        }

        request = self.factory.post(
            "/api/agent/diagnosis",
            {"ticket_id": str(self.ticket_id)},
            format="json",
            HTTP_AUTHORIZATION="Bearer valid-token"
        )
        response = views.agent_diagnosis_view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["affected_system"], "VPN Service")
        self.assertEqual(response.data["diagnosis_confidence"], 0.85)

    @patch("apps.agents.views.AccessToken")
    @patch("apps.agents.views.users_collection")
    @patch("apps.agents.views.tickets_collection")
    @patch("apps.agents.views.create_jira_issue")
    def test_jira_create_view(self, mock_create_jira, mock_tickets, mock_users, mock_access_token):
        mock_access_token.return_value = {"user_id": str(self.admin_id)}
        mock_users.find_one.return_value = self.mock_user
        mock_tickets.find_one.return_value = self.mock_ticket
        
        mock_create_jira.return_value = {
            "_id": ObjectId(),
            "ticket_id": str(self.ticket_id),
            "jira_issue_key": "SP-1050",
            "jira_status": "To Do"
        }

        request = self.factory.post(
            "/api/jira/tickets",
            {"ticket_id": str(self.ticket_id)},
            format="json",
            HTTP_AUTHORIZATION="Bearer valid-token"
        )
        response = views.jira_create_view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["jira_issue_key"], "SP-1050")

    @patch("apps.agents.views.AccessToken")
    @patch("apps.agents.views.users_collection")
    @patch("apps.agents.views.get_jira_mapping")
    @patch("apps.agents.views.update_jira_issue")
    def test_jira_detail_or_update_view(self, mock_update_jira, mock_get_jira, mock_users, mock_access_token):
        mock_access_token.return_value = {"user_id": str(self.admin_id)}
        mock_users.find_one.return_value = self.mock_user
        
        mock_get_jira.return_value = {
            "_id": ObjectId(),
            "ticket_id": str(self.ticket_id),
            "jira_issue_key": "SP-1050",
            "jira_status": "To Do"
        }
        
        mock_update_jira.return_value = {
            "_id": ObjectId(),
            "ticket_id": str(self.ticket_id),
            "jira_issue_key": "SP-1050",
            "jira_status": "In Progress"
        }

        # Test GET
        request_get = self.factory.get(
            f"/api/jira/tickets/{self.ticket_id}",
            HTTP_AUTHORIZATION="Bearer valid-token"
        )
        response_get = views.jira_detail_or_update_view(request_get, ticket_id=str(self.ticket_id))
        self.assertEqual(response_get.status_code, status.HTTP_200_OK)
        self.assertEqual(response_get.data["jira_status"], "To Do")

        # Test PUT
        request_put = self.factory.put(
            f"/api/jira/tickets/{self.ticket_id}",
            {"jira_status": "In Progress"},
            format="json",
            HTTP_AUTHORIZATION="Bearer valid-token"
        )
        response_put = views.jira_detail_or_update_view(request_put, ticket_id=str(self.ticket_id))
        self.assertEqual(response_put.status_code, status.HTTP_200_OK)
        self.assertEqual(response_put.data["jira_status"], "In Progress")

    @patch("apps.agents.views.AccessToken")
    @patch("apps.agents.views.users_collection")
    @patch("apps.agents.views.tickets_collection")
    @patch("apps.agents.views.send_resolution_email")
    def test_email_resolution_view(self, mock_send_email, mock_tickets, mock_users, mock_access_token):
        mock_access_token.return_value = {"user_id": str(self.admin_id)}
        mock_users.find_one.return_value = self.mock_user
        mock_tickets.find_one.return_value = self.mock_ticket
        
        mock_send_email.return_value = {
            "_id": "mock-email-id",
            "ticket_id": str(self.ticket_id),
            "recipient": "client@example.com",
            "subject": "SupportPilot Resolution Action Required",
            "status": "SENT"
        }

        request = self.factory.post(
            "/api/email/resolution",
            {"ticket_id": str(self.ticket_id), "resolution_text": "Step 1. Check VPN status."},
            format="json",
            HTTP_AUTHORIZATION="Bearer valid-token"
        )
        response = views.email_resolution_view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "SENT")

    @patch("apps.agents.services.orchestrator._call_ollama_safe")
    @patch("apps.agents.services.orchestrator.retrieve_for_ticket")
    @patch("apps.agents.services.orchestrator.tickets_collection")
    @patch("apps.agents.services.orchestrator.agent_workflows_collection")
    @patch("apps.agents.services.orchestrator.agent_executions_collection")
    @patch("apps.agents.services.orchestrator.ticket_responses_collection")
    @patch("apps.agents.services.orchestrator.create_jira_issue")
    @patch("apps.agents.services.orchestrator.send_resolution_email")
    def test_full_orchestration_loop_success(self, mock_email, mock_jira, mock_responses, mock_execs, mock_workflows, mock_tickets, mock_retrieve, mock_call_llm):
        """
        Verify that the orchestrator starts, executes diagnosis, retrieval, resolution,
        evaluates metrics, and marks the workflow completed.
        """
        mock_tickets.find_one.return_value = self.mock_ticket
        mock_workflows.insert_one.return_value = MagicMock(inserted_id=ObjectId())
        
        # Mock retrieval agent
        mock_retrieve.return_value = {
            "context": "Knowledge base excerpt [SOURCE:KB-NET#0]",
            "results": [{"article_id": "KB-NET", "rerank_score": 0.90}],
            "queries": ["VPN connection troubleshooting"]
        }

        # Mock LLM calls (Diagnosis first, then Resolution)
        mock_call_llm.side_effect = [
            # Diagnosis return
            {
                "affected_system": "VPN client",
                "likely_causes": ["Incorrect connection profile"],
                "missing_information": [],
                "diagnosis_confidence": 0.85
            },
            # Resolution return
            {
                "sufficient_context": True,
                "summary": "Auto resolved summary details.",
                "steps": [{"order": 1, "instruction": "Check configuration settings.", "sources": ["KB-NET#0"], "requires_approval": False}],
                "sources": ["KB-NET#0"],
                "resolution_confidence": 0.85
            }
        ]

        mock_responses.insert_one.return_value = MagicMock(inserted_id=ObjectId())
        mock_workflows.find_one.return_value = {
            "_id": ObjectId(),
            "ticket_id": str(self.ticket_id),
            "workflow_status": "COMPLETED",
            "current_agent": "Done",
            "final_confidence": 0.85
        }
        
        workflow = start_workflow_orchestration(self.ticket_id)
        self.assertEqual(workflow["workflow_status"], "COMPLETED")
        self.assertEqual(workflow["final_confidence"], 0.85)
