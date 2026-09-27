from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory

from apps.tickets import services, views
from bson import ObjectId


class TicketBackgroundJobTests(SimpleTestCase):
    @patch("apps.agents.orchestrator.execute_orchestration_pipeline", return_value={"status": "COMPLETED"})
    @patch.object(services, "auto_assign_ticket", return_value=None)
    @patch.object(services, "send_ticket_created_email")
    @patch.object(services.tickets_collection, "update_one")
    @patch.object(services.tickets_collection, "find_one")
    @patch("apps.tickets.classification.pipeline.classify_ticket")
    def test_customer_confirmation_sends_after_classification_is_persisted(
        self, classify, find_one, update_one, send_email, _assign, _orchestrate
    ):
        initial_ticket = {
            "ticket_id": "IT-2026-000002",
            "subject": "CRM unavailable",
            "description": "CRM requests are failing.",
            "requester": {"email": "customer@example.com"},
            "assignee": None,
        }
        classified_ticket = {
            **initial_ticket,
            "category": "APPLICATION",
            "subcategory": "CRM",
            "severity": "HIGH",
            "priority": "P1",
        }
        find_one.side_effect = [initial_ticket, classified_ticket, classified_ticket]
        classify.return_value = {
            "category": {"value": "APPLICATION"},
            "subcategory": {"value": "CRM"},
            "severity": {"value": "HIGH"},
            "priority": "P1",
            "sla": {},
            "queue": "APPLICATION_SUPPORT",
        }

        def assert_classified_email(*, ticket):
            self.assertTrue(update_one.called)
            self.assertEqual(ticket["severity"], "HIGH")
            self.assertEqual(ticket["priority"], "P1")

        send_email.side_effect = assert_classified_email

        services.classify_and_update_ticket(initial_ticket["ticket_id"])

        send_email.assert_called_once()

    def test_ticket_api_persists_then_enqueues_without_running_classification(self):
        factory = APIRequestFactory()
        user_id = ObjectId()
        ticket = {"ticket_id": "IT-2026-000001", "assignee": None}
        request = factory.post("/api/tickets/", {
            "subject": "VPN connection unavailable",
            "description": "Cannot connect to VPN.",
            "affected_scope": "JUST_ME",
            "work_blocked": "YES",
        }, format="json", HTTP_AUTHORIZATION="Bearer test-access-token")
        with patch.object(views, "AccessToken", return_value={"user_id": str(user_id)}), patch.object(
            views, "ObjectId", return_value=user_id
        ), patch.object(
            views.users_collection, "find_one", return_value={"_id": user_id, "username": "customer", "email": "customer@example.com"}
        ), patch.object(
            views, "create_ticket", return_value=ticket
        ) as create, patch.object(
            views, "enqueue_classification"
        ) as enqueue, patch.object(
            views, "create_notification"
        ), patch.object(
            views, "classify_and_update_ticket", create=True
        ) as classify:
            response = views.create_ticket_view(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["ticket"]["ticket_id"], ticket["ticket_id"])
        create.assert_called_once()
        enqueue.assert_called_once_with(ticket["ticket_id"])
        classify.assert_not_called()

    @patch.object(services.ticket_jobs_collection, "update_one")
    def test_enqueue_persists_a_deduplicated_mongo_job(self, update_one):
        services.enqueue_classification("IT-2026-000001")
        args, kwargs = update_one.call_args
        self.assertEqual(args[0]["_id"], "ticket-processing:IT-2026-000001")
        self.assertEqual(args[1]["$setOnInsert"]["status"], "queued")
        self.assertTrue(kwargs["upsert"])

    @patch.object(services.ticket_jobs_collection, "find_one_and_update")
    def test_claim_uses_atomic_queue_claim_and_expired_lease_recovery(self, claim):
        claim.return_value = {"_id": "ticket-processing:T1", "ticket_id": "T1"}
        result = services.claim_ticket_job()
        self.assertEqual(result["ticket_id"], "T1")
        query = claim.call_args.args[0]
        self.assertEqual(query["job_type"], "ticket_processing")
        self.assertEqual(query["$or"][0], {"status": "queued"})
        self.assertIn("locked_until", query["$or"][1])

    @patch.object(services.ticket_jobs_collection, "update_one")
    @patch.object(services, "classify_and_update_ticket")
    def test_successful_worker_run_marks_job_complete(self, classify, update_one):
        job = {"_id": "ticket-processing:T1", "ticket_id": "T1", "attempts": 1}
        services.run_ticket_job(job)
        classify.assert_called_once_with("T1")
        self.assertEqual(update_one.call_args.args[0]["status"], "processing")
        self.assertEqual(update_one.call_args.args[1]["$set"]["status"], "completed")

    @patch.object(services.ticket_jobs_collection, "update_one")
    @patch.object(services, "classify_and_update_ticket", return_value={"m3": {"status": "FAILED", "reason": "Ollama unavailable"}})
    def test_m3_failure_is_not_reported_as_a_successful_job(self, _classify, update_one):
        services.run_ticket_job({"_id": "job-1", "ticket_id": "T1", "attempts": 1})
        update = update_one.call_args.args[1]["$set"]
        self.assertEqual(update["status"], "completed_with_errors")
        self.assertEqual(update["last_error"], "Ollama unavailable")

    @patch.object(services.ticket_jobs_collection, "update_one")
    @patch.object(services, "classify_and_update_ticket", side_effect=RuntimeError("temporary failure"))
    def test_worker_failure_requeues_then_stops_at_retry_limit(self, _classify, update_one):
        services.run_ticket_job({"_id": "job-1", "ticket_id": "T1", "attempts": 1})
        self.assertEqual(update_one.call_args.args[1]["$set"]["status"], "queued")
        services.run_ticket_job({"_id": "job-1", "ticket_id": "T1", "attempts": 3})
        self.assertEqual(update_one.call_args.args[1]["$set"]["status"], "failed")
