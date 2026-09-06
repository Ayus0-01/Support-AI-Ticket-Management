from datetime import datetime, timezone

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
        "is_active": True,
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
    result = users_collection.insert_one(user)
    user["_id"] = result.inserted_id

    tokens = get_tokens_for_user(user)

    return {
        "success": True,
        "message": "User registered successfully.",
        "access": tokens["access"],
        "refresh": tokens["refresh"],
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
