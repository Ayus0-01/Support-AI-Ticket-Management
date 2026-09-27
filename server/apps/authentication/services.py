from datetime import datetime, timedelta, timezone
import hashlib
import secrets

from django.contrib.auth.hashers import check_password, make_password
from rest_framework_simplejwt.tokens import RefreshToken

from AIticket.db import users_collection
from .constants import USER_ROLES


def _utc_now():
    return datetime.now(timezone.utc)


def _find_duplicate_account(*, username, email):
    return users_collection.find_one(
        {
            "$or": [
                {"email": email},
                {"username": username},
            ]
        }
    )


def _duplicate_message(existing_user, *, username, email):
    if existing_user.get("email") == email:
        return "Email already exists."
    if existing_user.get("username") == username:
        return "Username already exists."
    return "An account with those details already exists."


def _build_user_document(data, *, role):
    return {
        "username": data["username"],
        "email": data["email"],
        "mobile": data.get("mobile", ""),
        "role": role,
        "specialties": list(data.get("specialties", [])) if role == "Agent" else [],
        "is_active": True,
        # Staff accounts provisioned by an administrator are trusted. Public
        # registrations are explicitly unverified until the mailbox is proven.
        "email_verified": role != "User",
        "created_at": _utc_now(),
        "last_login_at": None,
        "password": make_password(data["password"]),
    }


def register_service(data):
    existing_user = _find_duplicate_account(
        username=data["username"],
        email=data["email"],
    )

    if existing_user:
        return {
            "success": False,
            "message": _duplicate_message(
                existing_user,
                username=data["username"],
                email=data["email"],
            ),
        }

    user = _build_user_document(data, role="User")
    token = secrets.token_urlsafe(32)
    user["email_verification_token_hash"] = hashlib.sha256(token.encode()).hexdigest()
    user["email_verification_expires_at"] = _utc_now() + timedelta(hours=24)
    result = users_collection.insert_one(user)
    user["_id"] = result.inserted_id

    return {
        "success": True,
        "message": "Registration successful. Check your email for a verification link before signing in.",
        "user": user,
        "verification_token": token,
    }


def create_managed_user(data):
    role = data["role"]

    if role not in USER_ROLES:
        return {"success": False, "message": "Unsupported account role."}

    existing_user = _find_duplicate_account(
        username=data["username"],
        email=data["email"],
    )

    if existing_user:
        return {
            "success": False,
            "message": _duplicate_message(
                existing_user,
                username=data["username"],
                email=data["email"],
            ),
        }

    user = _build_user_document(data, role=role)
    result = users_collection.insert_one(user)
    user["_id"] = result.inserted_id

    return {"success": True, "user": user}


def count_active_admins():
    return users_collection.count_documents(
        {
            "role": "Admin",
            "$or": [
                {"is_active": True},
                {"is_active": {"$exists": False}},
            ],
        }
    )


def update_managed_user(*, actor_id, target_user, updates):
    if target_user["_id"] == actor_id:
        return {
            "success": False,
            "status_code": 400,
            "message": "Administrators cannot change their own role or account status.",
        }

    target_is_active = target_user.get("is_active", True)
    target_role = target_user.get("role", "User")
    next_role = updates.get("role", target_role)
    next_is_active = updates.get("is_active", target_is_active)

    if updates.get("specialties") and next_role != "Agent":
        return {
            "success": False,
            "status_code": 400,
            "message": "Specialties can only be assigned to Agent accounts.",
        }
    if target_role == "Agent" and next_role != "Agent":
        updates["specialties"] = []

    removes_active_admin_access = (
        target_role == "Admin"
        and target_is_active
        and (next_role != "Admin" or not next_is_active)
    )

    if removes_active_admin_access and count_active_admins() <= 1:
        return {
            "success": False,
            "status_code": 400,
            "message": "The last active Admin account cannot be changed or deactivated.",
        }

    users_collection.update_one(
        {"_id": target_user["_id"]},
        {"$set": updates},
    )

    return {
        "success": True,
        "user": {**target_user, **updates},
    }


def get_tokens_for_user(user):
    refresh = RefreshToken()
    refresh["user_id"] = str(user["_id"])
    refresh["email"] = user["email"]

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def login_service(data):
    user = users_collection.find_one({"email": data["email"]})

    if not user or not check_password(data["password"], user.get("password", "")):
        return {
            "success": False,
            "message": "Invalid email or password.",
        }

    # Historical staff accounts were provisioned internally before this field
    # existed. Customer accounts without an explicit verified flag remain
    # unverified by default.
    if not user.get("email_verified", user.get("role") != "User"):
        return {
            "success": False,
            "message": "Verify your email address before signing in.",
        }

    if not user.get("is_active", True):
        return {
            "success": False,
            "message": "This account is inactive. Contact an administrator.",
        }

    users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login_at": _utc_now()}},
    )

    tokens = get_tokens_for_user(user)

    return {
        "success": True,
        "message": "Login Successful",
        "access": tokens["access"],
        "refresh": tokens["refresh"],
    }


def verify_email(token):
    """Consume a single-use, expiring mailbox verification token."""
    import hashlib

    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    # PyMongo's default codec returns naive UTC datetimes.
    now = _utc_now().replace(tzinfo=None)
    user = users_collection.find_one({"email_verification_token_hash": token_hash})
    if not user:
        return {"success": False, "message": "This verification link is invalid or has already been used."}
    if user.get("email_verified"):
        return {"success": True, "message": "This email address is already verified."}
    expiry = user.get("email_verification_expires_at")
    if expiry and expiry.tzinfo is not None:
        expiry = expiry.astimezone(timezone.utc).replace(tzinfo=None)
    if not expiry or expiry <= now:
        return {"success": False, "message": "This verification link has expired. Request a new link."}

    result = users_collection.update_one(
        {
            "_id": user["_id"],
            "email_verification_token_hash": token_hash,
            "email_verified": {"$ne": True},
            "email_verification_expires_at": {"$gt": now},
        },
        {"$set": {"email_verified": True}, "$unset": {
            "email_verification_token_hash": "",
            "email_verification_expires_at": "",
        }},
    )
    if result.modified_count:
        return {"success": True, "message": "Email address verified. You can now sign in."}
    return {"success": False, "message": "This verification link is invalid or has expired."}


def issue_email_verification(email):
    """Issue a fresh verification token only for an unverified customer account."""
    user = users_collection.find_one({"email": email})
    if (
        not user
        or user.get("role", "User") != "User"
        or user.get("email_verified") is True
        or not user.get("is_active", True)
    ):
        return None

    token = secrets.token_urlsafe(32)
    result = users_collection.update_one(
        {"_id": user["_id"], "email_verified": {"$ne": True}},
        {"$set": {
            "email_verification_token_hash": hashlib.sha256(token.encode()).hexdigest(),
            "email_verification_expires_at": _utc_now() + timedelta(hours=24),
        }},
    )
    return token if result.modified_count else None
