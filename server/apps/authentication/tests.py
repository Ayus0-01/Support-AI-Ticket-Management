from unittest.mock import patch, MagicMock
from bson import ObjectId
from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status

from apps.authentication import views


class AdminUserManagementTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin_id = ObjectId()
        self.non_admin_id = ObjectId()

    def get_mock_admin(self):
        return {
            "_id": self.admin_id,
            "username": "admin_user",
            "email": "admin@example.com",
            "role": "Admin",
            "status": "Active"
        }

    def get_mock_user(self):
        return {
            "_id": self.non_admin_id,
            "username": "regular_user",
            "email": "user@example.com",
            "role": "User",
            "status": "Active"
        }

    @patch("apps.authentication.views.AccessToken")
    @patch("apps.authentication.views.users_collection")
    def test_admin_can_list_users(self, mock_users_col, mock_access_token):
        # Setup mock authentication
        mock_access_token.return_value = {"user_id": str(self.admin_id)}
        mock_users_col.find_one.return_value = self.get_mock_admin()
        
        # Setup mock find query returning multiple users
        mock_users_col.find.return_value = [
            self.get_mock_admin(),
            self.get_mock_user()
        ]

        request = self.factory.get(
            "/api/auth/admin/users/",
            HTTP_AUTHORIZATION="Bearer admin-token"
        )
        response = views.admin_users_view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Ensure password hash and credentials are NOT present in output
        for u in response.data:
            self.assertNotIn("password", u)
            self.assertNotIn("password_hash", u)
            self.assertIn("id", u)
            self.assertIn("username", u)
            self.assertIn("email", u)

    @patch("apps.authentication.views.AccessToken")
    @patch("apps.authentication.views.users_collection")
    def test_non_admin_cannot_list_users(self, mock_users_col, mock_access_token):
        mock_access_token.return_value = {"user_id": str(self.non_admin_id)}
        mock_users_col.find_one.return_value = self.get_mock_user()

        request = self.factory.get(
            "/api/auth/admin/users/",
            HTTP_AUTHORIZATION="Bearer user-token"
        )
        response = views.admin_users_view(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["message"], "Admin access required.")

    @patch("apps.authentication.views.make_password", return_value="hashed_password")
    @patch("apps.authentication.views.AccessToken")
    @patch("apps.authentication.views.users_collection")
    def test_admin_can_create_user_agent_admin(self, mock_users_col, mock_access_token, mock_make_pass):
        mock_access_token.return_value = {"user_id": str(self.admin_id)}
        
        # First call to find_one is auth check, subsequent can be uniqueness checks
        mock_users_col.find_one.side_effect = [
            self.get_mock_admin(), # Auth check
            None,                  # Email check (unique)
            None                   # Username check (unique)
        ]
        
        mock_users_col.insert_one.return_value = MagicMock(inserted_id=ObjectId())

        request_data = {
            "username": "new_agent",
            "email": "agent@example.com",
            "password": "SecretPassword123!",
            "role": "Agent",
            "status": "Active"
        }
        
        request = self.factory.post(
            "/api/auth/admin/users/",
            request_data,
            format="json",
            HTTP_AUTHORIZATION="Bearer admin-token"
        )
        response = views.admin_users_view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], "new_agent")
        self.assertEqual(response.data["role"], "Agent")
        self.assertNotIn("password", response.data)

    @patch("apps.authentication.views.AccessToken")
    @patch("apps.authentication.views.users_collection")
    def test_non_admin_cannot_create_users(self, mock_users_col, mock_access_token):
        mock_access_token.return_value = {"user_id": str(self.non_admin_id)}
        mock_users_col.find_one.return_value = self.get_mock_user()

        request_data = {
            "username": "hacker_agent",
            "email": "hacker@example.com",
            "password": "Password123!",
            "role": "Agent"
        }
        request = self.factory.post(
            "/api/auth/admin/users/",
            request_data,
            format="json",
            HTTP_AUTHORIZATION="Bearer user-token"
        )
        response = views.admin_users_view(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch("apps.authentication.views.AccessToken")
    @patch("apps.authentication.views.users_collection")
    def test_update_role_and_status(self, mock_users_col, mock_access_token):
        mock_access_token.return_value = {"user_id": str(self.admin_id)}
        target_id = ObjectId()
        
        mock_users_col.find_one.side_effect = [
            self.get_mock_admin(), # Auth check
            {                      # Target user
                "_id": target_id,
                "username": "target_user",
                "email": "target@example.com",
                "role": "User",
                "status": "Active"
            },
            {                      # Updated user returning
                "_id": target_id,
                "username": "target_user",
                "email": "target@example.com",
                "role": "Agent",
                "status": "Inactive"
            }
        ]

        request = self.factory.patch(
            f"/api/auth/admin/users/{target_id}/",
            {"role": "Agent", "status": "Inactive"},
            format="json",
            HTTP_AUTHORIZATION="Bearer admin-token"
        )
        response = views.admin_user_detail_view(request, str(target_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["role"], "Agent")
        self.assertEqual(response.data["status"], "Inactive")

    @patch("apps.authentication.views.AccessToken")
    @patch("apps.authentication.views.users_collection")
    def test_self_protection_prevents_last_admin_demotion(self, mock_users_col, mock_access_token):
        # Admin trying to deactivate self or demote self
        mock_access_token.return_value = {"user_id": str(self.admin_id)}
        
        mock_users_col.find_one.side_effect = [
            self.get_mock_admin(), # Auth check
            self.get_mock_admin(), # Target user (self)
        ]
        
        # Mock count of documents for active admins returning 1 (only this admin remains)
        mock_users_col.count_documents.return_value = 1

        request = self.factory.patch(
            f"/api/auth/admin/users/{self.admin_id}/",
            {"role": "User"},
            format="json",
            HTTP_AUTHORIZATION="Bearer admin-token"
        )
        response = views.admin_user_detail_view(request, str(self.admin_id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["message"],
            "Cannot deactivate or demote the only remaining Admin account."
        )

    @patch("apps.authentication.views.AccessToken")
    @patch("apps.authentication.views.users_collection")
    def test_deactivated_user_cannot_fetch_profile(self, mock_users_col, mock_access_token):
        mock_access_token.return_value = {"user_id": str(self.non_admin_id)}
        mock_users_col.find_one.return_value = {
            "_id": self.non_admin_id,
            "username": "inactive_user",
            "email": "inactive@example.com",
            "role": "User",
            "status": "Inactive"
        }

        request = self.factory.get(
            "/api/auth/me/",
            HTTP_AUTHORIZATION="Bearer user-token"
        )
        response = views.me(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["message"], "User account is deactivated.")
