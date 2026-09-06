from django.http import JsonResponse
from rest_framework_simplejwt.tokens import AccessToken
from bson import ObjectId

from AIticket.db import users_collection


class ActiveAccountMiddleware:
    """Reject API requests made with a token for a deactivated account."""

    public_auth_paths = {
        "/api/auth/login/",
        "/api/auth/register/",
        "/api/auth/refresh/",
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.method == "OPTIONS"
            or not request.path.startswith("/api/")
            or request.path in self.public_auth_paths
        ):
            return self.get_response(request)

        auth_header = request.headers.get("Authorization", "")
        parts = auth_header.split(" ")

        if len(parts) != 2 or parts[0] != "Bearer":
            return self.get_response(request)

        try:
            user_id = AccessToken(parts[1])["user_id"]
            user = users_collection.find_one({"_id": ObjectId(user_id)})
        except Exception:
            return self.get_response(request)

        if user and not user.get("is_active", True):
            return JsonResponse(
                {"message": "This account is inactive. Contact an administrator."},
                status=403,
            )

        return self.get_response(request)
