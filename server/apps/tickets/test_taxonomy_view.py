from unittest.mock import patch

from bson import ObjectId
from django.test import SimpleTestCase
from django.urls import resolve
from rest_framework.test import APIRequestFactory

from apps.tickets import views
from apps.tickets.classification.subcategory_classifier import (
    CATEGORY_SUBCATEGORIES,
)


class TicketTaxonomyViewTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_taxonomy_route_returns_the_active_selectable_categories(self):
        user_id = ObjectId()
        request = self.factory.get(
            "/api/tickets/taxonomy/",
            HTTP_AUTHORIZATION="Bearer test-token",
        )

        with patch.object(
            views,
            "AccessToken",
            return_value={"user_id": str(user_id)},
        ), patch.object(
            views.users_collection,
            "find_one",
            return_value={"_id": user_id, "role": "User"},
        ):
            response = views.ticket_taxonomy_view(request)

        expected_categories = sorted(
            category
            for category, subcategories in CATEGORY_SUBCATEGORIES.items()
            if subcategories
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["categories"], expected_categories)

    def test_taxonomy_route_is_registered_before_ticket_detail(self):
        match = resolve("/api/tickets/taxonomy/")

        self.assertEqual(match.func, views.ticket_taxonomy_view)
