from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from bson import ObjectId
from django.test import SimpleTestCase

from apps.authentication import services


class EmailVerificationServiceTests(SimpleTestCase):
    @patch.object(services.users_collection, "update_one")
    @patch.object(services.users_collection, "find_one")
    def test_resend_issues_new_hashed_token_for_existing_unverified_customer(self, find_one, update_one):
        find_one.return_value = {
            "_id": ObjectId(),
            "role": "User",
            "email_verified": False,
            "is_active": True,
        }
        update_one.return_value = MagicMock(modified_count=1)

        token = services.issue_email_verification("customer@example.com")

        query, update = update_one.call_args.args
        self.assertIsInstance(token, str)
        self.assertNotEqual(update["$set"]["email_verification_token_hash"], token)
        self.assertEqual(len(update["$set"]["email_verification_token_hash"]), 64)
        self.assertEqual(query["email_verified"], {"$ne": True})
        self.assertGreater(update["$set"]["email_verification_expires_at"], datetime.now().astimezone())

    @patch.object(services.users_collection, "update_one")
    @patch.object(services.users_collection, "find_one")
    def test_resend_does_not_issue_tokens_for_verified_or_staff_accounts(self, find_one, update_one):
        find_one.return_value = {"_id": ObjectId(), "role": "User", "email_verified": True}
        self.assertIsNone(services.issue_email_verification("customer@example.com"))
        find_one.return_value = {"_id": ObjectId(), "role": "Agent", "email_verified": True}
        self.assertIsNone(services.issue_email_verification("agent@example.com"))
        find_one.return_value = None
        self.assertIsNone(services.issue_email_verification("missing@example.com"))
        update_one.assert_not_called()

    @patch.object(services.users_collection, "insert_one")
    @patch.object(services, "_find_duplicate_account", return_value=None)
    def test_registration_stores_only_token_hash_and_issues_no_jwt(self, _duplicate, insert):
        insert.return_value = MagicMock(inserted_id=ObjectId())
        result = services.register_service({
            "username": "new-user",
            "email": "new@example.com",
            "password": "a-test-password",
        })

        document = insert.call_args.args[0]
        self.assertTrue(result["success"])
        self.assertTrue(document["email_verified"] is False)
        self.assertNotEqual(document["email_verification_token_hash"], result["verification_token"])
        self.assertNotIn("access", result)
        self.assertNotIn("refresh", result)

    @patch.object(services.users_collection, "update_one")
    @patch.object(services.users_collection, "find_one")
    def test_valid_token_is_consumed_and_verifies_account(self, find_one, update_one):
        user_id = ObjectId()
        now = datetime.utcnow()
        raw_token = "opaque-verification-token"
        import hashlib
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        find_one.return_value = {
            "_id": user_id,
            "email_verified": False,
            "email_verification_token_hash": token_hash,
            "email_verification_expires_at": now + timedelta(hours=1),
        }
        update_one.return_value = MagicMock(modified_count=1)

        result = services.verify_email(raw_token)

        self.assertTrue(result["success"])
        self.assertIn("email_verified", update_one.call_args.args[1]["$set"])
        self.assertIn("email_verification_token_hash", update_one.call_args.args[1]["$unset"])
        find_one.return_value = None
        self.assertFalse(services.verify_email(raw_token)["success"])

    @patch.object(services.users_collection, "update_one")
    @patch.object(services.users_collection, "find_one")
    def test_expired_and_unknown_tokens_are_rejected(self, find_one, update_one):
        find_one.return_value = {
            "_id": ObjectId(),
            "email_verified": False,
            "email_verification_expires_at": datetime.utcnow() - timedelta(seconds=1),
        }
        expired = services.verify_email("expired-token")
        self.assertFalse(expired["success"])
        update_one.assert_not_called()

        find_one.return_value = None
        invalid = services.verify_email("unknown-token")
        self.assertFalse(invalid["success"])

    @patch.object(services, "get_tokens_for_user")
    @patch.object(services.users_collection, "update_one")
    @patch.object(services.users_collection, "find_one")
    def test_unverified_user_cannot_login_but_verified_user_gets_jwt(self, find_one, _update, tokens):
        from django.contrib.auth.hashers import make_password

        user = {
            "_id": ObjectId(),
            "email": "customer@example.com",
            "password": make_password("correct-password"),
            "role": "User",
            "is_active": True,
            "email_verified": False,
        }
        find_one.return_value = user
        denied = services.login_service({"email": user["email"], "password": "correct-password"})
        self.assertFalse(denied["success"])
        tokens.assert_not_called()

        user["email_verified"] = True
        tokens.return_value = {"access": "access-token", "refresh": "refresh-token"}
        allowed = services.login_service({"email": user["email"], "password": "correct-password"})
        self.assertTrue(allowed["success"])
        self.assertEqual(allowed["access"], "access-token")
