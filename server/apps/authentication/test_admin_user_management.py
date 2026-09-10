from contextlib import contextmanager
from secrets import token_urlsafe
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from bson import ObjectId
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase
from django.contrib.auth.hashers import make_password
from rest_framework.test import APIRequestFactory

from apps.authentication import services, views
from apps.authentication.constants import USER_ROLES
from apps.authentication.middleware import ActiveAccountMiddleware


def test_password():
    return f"Test-{token_urlsafe(24)}-A1"


class AdminUserManagementViewTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin_id = ObjectId()
        self.admin = self._user(self.admin_id, role="Admin")

    @staticmethod
    def _user(user_id, *, role="User", is_active=True):
        return {
            "_id": user_id,
            "username": f"account-{str(user_id)[-6:]}",
            "email": f"account-{str(user_id)[-6:]}@example.com",
            "role": role,
            "is_active": is_active,
            "password": "hashed-password-must-never-be-exposed",
            "refresh": "must-never-be-exposed",
        }

    def _admin_request(self, method, path, data=None):
        request_method = getattr(self.factory, method)
        return request_method(
            path,
            data or {},
            format="json",
            HTTP_AUTHORIZATION="Bearer test-token",
        )

    @contextmanager
    def _authenticated_context(self, collection):
        with patch.object(views, "users_collection", collection), patch.object(
            services,
            "users_collection",
            collection,
        ), patch.object(
                views,
                "AccessToken",
                return_value={"user_id": str(self.admin_id)},
            ):
            yield

    def test_admin_can_list_database_users_with_safe_fields_only(self):
        collection = MagicMock()
        listed_user = self._user(ObjectId(), role="Agent")
        collection.find_one.return_value = self.admin
        collection.find.return_value.sort.return_value = [listed_user]
        request = self._admin_request("get", "/api/auth/admin/users/")

        with self._authenticated_context(collection):
            response = views.admin_users(request)
            response.render()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["roles"], USER_ROLES)
        self.assertEqual(len(response.data["users"]), 1)
        safe_user = response.data["users"][0]
        self.assertEqual(
            set(safe_user),
            {"id", "username", "email", "role", "is_active", "created_at", "last_login_at"},
        )
        self.assertNotIn("password", safe_user)
        self.assertNotIn("refresh", safe_user)

    def test_non_admin_cannot_list_users(self):
        collection = MagicMock()
        collection.find_one.return_value = self._user(self.admin_id, role="Agent")
        request = self._admin_request("get", "/api/auth/admin/users/")

        with self._authenticated_context(collection):
            response = views.admin_users(request)

        self.assertEqual(response.status_code, 403)
        collection.find.assert_not_called()

    def test_admin_can_create_each_supported_role_without_exposing_password(self):
        collection = MagicMock()

        with self._authenticated_context(collection), patch.object(
            services,
            "make_password",
            return_value="stored-hash",
        ):
            for role in USER_ROLES:
                with self.subTest(role=role):
                    collection.reset_mock()
                    collection.find_one.side_effect = [self.admin, None]
                    collection.insert_one.return_value = SimpleNamespace(inserted_id=ObjectId())
                    password = test_password()
                    request = self._admin_request(
                        "post",
                        "/api/auth/admin/users/",
                        {
                            "username": f"created-{role.lower().replace(' ', '-')}",
                            "email": f"created-{role.lower().replace(' ', '-')}@example.com",
                            "password": password,
                            "role": role,
                        },
                    )

                    response = views.admin_users(request)
                    response.render()

                    self.assertEqual(response.status_code, 201)
                    self.assertEqual(response.data["user"]["role"], role)
                    self.assertNotIn("password", response.data["user"])
                    self.assertNotIn("stored-hash", response.content.decode())
                    stored_user = collection.insert_one.call_args.args[0]
                    self.assertEqual(stored_user["role"], role)
                    self.assertTrue(stored_user["is_active"])

    def test_non_admin_cannot_create_an_elevated_account(self):
        collection = MagicMock()
        collection.find_one.return_value = self._user(self.admin_id, role="User")
        password = test_password()
        request = self._admin_request(
            "post",
            "/api/auth/admin/users/",
            {
                "username": "attempted-admin",
                "email": "attempted-admin@example.com",
                "password": password,
                "role": "Admin",
            },
        )

        with self._authenticated_context(collection):
            response = views.admin_users(request)

        self.assertEqual(response.status_code, 403)
        collection.insert_one.assert_not_called()

    def test_admin_can_change_another_account_role_and_status(self):
        collection = MagicMock()
        target = self._user(ObjectId(), role="User", is_active=True)
        collection.find_one.side_effect = [self.admin, target]
        request = self._admin_request(
            "patch",
            f"/api/auth/admin/users/{target['_id']}/",
            {"role": "Agent", "is_active": False},
        )

        with self._authenticated_context(collection):
            response = views.admin_user_detail(request, str(target["_id"]))
            response.render()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["user"]["role"], "Agent")
        self.assertFalse(response.data["user"]["is_active"])
        collection.update_one.assert_called_once_with(
            {"_id": target["_id"]},
            {"$set": {"role": "Agent", "is_active": False}},
        )

    def test_non_admin_cannot_change_another_account(self):
        collection = MagicMock()
        target = self._user(ObjectId(), role="User")
        collection.find_one.return_value = self._user(self.admin_id, role="Agent")
        request = self._admin_request(
            "patch",
            f"/api/auth/admin/users/{target['_id']}/",
            {"role": "Admin"},
        )

        with self._authenticated_context(collection):
            response = views.admin_user_detail(request, str(target["_id"]))

        self.assertEqual(response.status_code, 403)
        collection.update_one.assert_not_called()

    def test_admin_cannot_change_own_role_or_status(self):
        collection = MagicMock()
        collection.find_one.side_effect = [self.admin, self.admin]
        request = self._admin_request(
            "patch",
            f"/api/auth/admin/users/{self.admin_id}/",
            {"is_active": False},
        )

        with self._authenticated_context(collection):
            response = views.admin_user_detail(request, str(self.admin_id))

        self.assertEqual(response.status_code, 400)
        collection.update_one.assert_not_called()

    def test_last_active_admin_cannot_be_deactivated_or_demoted(self):
        collection = MagicMock()
        target = self._user(ObjectId(), role="Admin", is_active=True)
        collection.find_one.side_effect = [self.admin, target]
        request = self._admin_request(
            "patch",
            f"/api/auth/admin/users/{target['_id']}/",
            {"role": "User"},
        )

        with self._authenticated_context(collection), patch.object(
            services,
            "count_active_admins",
            return_value=1,
        ):
            response = views.admin_user_detail(request, str(target["_id"]))

        self.assertEqual(response.status_code, 400)
        collection.update_one.assert_not_called()

    def test_public_registration_cannot_create_an_elevated_account(self):
        collection = MagicMock()
        collection.find_one.return_value = None
        collection.insert_one.return_value = SimpleNamespace(inserted_id=ObjectId())
        password = test_password()

        with patch.object(services, "users_collection", collection), patch.object(
            services,
            "make_password",
            return_value="stored-hash",
        ), patch.object(
            services,
            "get_tokens_for_user",
            return_value={"access": "access", "refresh": "refresh"},
        ):
            result = services.register_service(
                {
                    "username": "public-account",
                    "email": "public-account@example.com",
                    "password": password,
                    "role": "Admin",
                }
            )

        self.assertTrue(result["success"])
        self.assertEqual(collection.insert_one.call_args.args[0]["role"], "User")


class AccountStatusSecurityTests(SimpleTestCase):
    def test_newly_created_managed_account_can_authenticate(self):
        collection = MagicMock()
        stored_accounts = {}

        def find_one(query):
            if "$or" in query:
                return None
            return stored_accounts.get(query.get("email"))

        def insert_one(document):
            user_id = ObjectId()
            stored_accounts[document["email"]] = {**document, "_id": user_id}
            return SimpleNamespace(inserted_id=user_id)

        collection.find_one.side_effect = find_one
        collection.insert_one.side_effect = insert_one
        password = test_password()

        with patch.object(services, "users_collection", collection), patch.object(
            services,
            "get_tokens_for_user",
            return_value={"access": "access", "refresh": "refresh"},
        ):
            created = services.create_managed_user(
                {
                    "username": "new-agent",
                    "email": "new-agent@example.com",
                    "password": password,
                    "role": "Agent",
                }
            )
            login = services.login_service(
                {"email": "new-agent@example.com", "password": password}
            )

        self.assertTrue(created["success"])
        self.assertTrue(login["success"])
        self.assertEqual(stored_accounts["new-agent@example.com"]["role"], "Agent")

    def test_inactive_account_cannot_login(self):
        collection = MagicMock()
        password = test_password()
        collection.find_one.return_value = {
            "_id": ObjectId(),
            "email": "inactive@example.com",
            "password": make_password(password),
            "is_active": False,
        }

        with patch.object(services, "users_collection", collection):
            result = services.login_service(
                {"email": "inactive@example.com", "password": password}
            )

        self.assertFalse(result["success"])
        self.assertIn("inactive", result["message"].lower())
        collection.update_one.assert_not_called()

    def test_middleware_rejects_an_inactive_token_holder(self):
        request = RequestFactory().get(
            "/api/tickets/my/",
            HTTP_AUTHORIZATION="Bearer test-token",
        )
        user_id = ObjectId()

        with patch(
            "apps.authentication.middleware.AccessToken",
            return_value={"user_id": str(user_id)},
        ), patch(
            "apps.authentication.middleware.users_collection.find_one",
            return_value={"_id": user_id, "is_active": False},
        ):
            response = ActiveAccountMiddleware(lambda _request: HttpResponse("ok"))(request)

        self.assertEqual(response.status_code, 403)
        self.assertIn(b"inactive", response.content.lower())
