from django.contrib.auth.hashers import make_password
from AIticket.db import users_collection


def register_service(data):

    existing_user = users_collection.find_one(
        {
            "email": data["email"]
        }
    )

    if existing_user:
        return {
            "success": False,
            "message": "Email already exists."
        }

    user = {
        "username": data["username"],
        "email": data["email"],
        "password": make_password(data["password"])
    }

    users_collection.insert_one(user)

    return {
        "success": True,
        "message": "User registered successfully."
    }
from django.contrib.auth.hashers import check_password

def login_service(data):

    user = users_collection.find_one(
        {
            "email": data["email"]
        }
    )

    if not user:
        return {
            "success": False,
            "message": "User does not exist."
        }

    if not check_password(
        data["password"],
        user["password"]
    ):
        return {
            "success": False,
            "message": "Invalid password."
        }

    return {
        "success": True,
        "user": user
    }