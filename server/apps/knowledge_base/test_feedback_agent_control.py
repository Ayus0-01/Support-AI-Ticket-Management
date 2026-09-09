from unittest.mock import patch

from bson import ObjectId
from django.test import SimpleTestCase

from apps.knowledge_base import review_service


class ResolutionFeedbackAgentControlTests(SimpleTestCase):
    def test_requester_confirmation_never_closes_the_ticket(self):
        requester_id = ObjectId()
        ticket_id = ObjectId()
        response_id = ObjectId()
        ticket = {
            "_id": ticket_id,
            "ticket_id": "TKT-FEEDBACK-001",
            "status": "In Progress",
            "requester": {"user_id": str(requester_id)},
        }
        response = {
            "_id": response_id,
            "ticket_id": ticket_id,
            "status": "SENT",
            "summary": "Restart the approved VPN client.",
        }
        feedback = {"_id": ObjectId(), "resolved_ticket": True}

        with patch.object(
            review_service,
            "get_ticket_response",
            return_value=response,
        ), patch.object(
            review_service.tickets_collection,
            "find_one",
            side_effect=[ticket, ticket],
        ), patch.object(
            review_service.resolution_feedback_collection,
            "find_one",
            return_value=None,
        ), patch.object(
            review_service,
            "create_resolution_feedback",
            return_value=feedback,
        ) as create_feedback, patch.object(
            review_service,
            "update_ticket_resolution_state",
        ) as update_resolution_state, patch.object(
            review_service,
            "add_ticket_comment",
        ) as add_comment, patch.object(
            review_service,
            "transition_ticket_status",
        ) as transition_status:
            result = review_service.submit_feedback(
                response_id=str(response_id),
                user_id=requester_id,
                was_helpful=True,
                comment="The connection works now.",
                user_role="User",
            )

        self.assertEqual(result["ticket"]["status"], "In Progress")
        create_feedback.assert_called_once_with(
            response_id=str(response_id),
            ticket_id=ticket_id,
            user_id=requester_id,
            was_helpful=True,
            comment="The connection works now.",
            resolved_ticket=True,
        )
        update_resolution_state.assert_called_once_with(
            ticket_id=ticket_id,
            resolution_status="CONFIRMED",
            response_id=response_id,
        )
        transition_status.assert_not_called()
        self.assertIn("Awaiting agent closure", add_comment.call_args.kwargs["comment"])
