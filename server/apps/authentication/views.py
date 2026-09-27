from bson import ObjectId
from decouple import config
from django.core.mail import send_mail
from rest_framework import serializers, status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken


from AIticket.db import users_collection
from .constants import USER_ROLES
from .serializers import (
    LoginSerializer,
    ManagedUserCreateSerializer,
    ManagedUserSerializer,
    ManagedUserUpdateSerializer,
    RegisterSerializer,
)
from .services import (
    create_managed_user,
    login_service,
    issue_email_verification,
    register_service,
    update_managed_user,
    verify_email as verify_email_service,
)
from apps.tickets.classification.subcategory_classifier import AGENT_SPECIALTY_CATEGORIES


SAFE_USER_PROJECTION = {
    "username": 1,
    "email": 1,
    "role": 1,
    "specialties": 1,
    "is_active": 1,
    "created_at": 1,
    "last_login_at": 1,
}


def _normalise_managed_user(user):
    """Apply compatibility defaults without exposing the raw user document."""

    return {
        "_id": user["_id"],
        "username": user.get("username", ""),
        "email": user.get("email", ""),
        "role": user.get("role") or "User",
        "specialties": user.get("specialties", []),
        "is_active": user.get("is_active", True),
        "created_at": user.get("created_at"),
        "last_login_at": user.get("last_login_at"),
    }


def _get_authenticated_user(request):
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return None, Response(
            {"message": "Authorization header missing."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    try:
        parts = auth_header.split(" ")
        if len(parts) != 2 or parts[0] != "Bearer":
            raise ValueError("Invalid Authorization header")

        user_id = AccessToken(parts[1])["user_id"]
        user = users_collection.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None, Response(
            {"message": "Invalid or expired token."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not user:
        return None, Response(
            {"message": "User not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    if not user.get("is_active", True):
        return None, Response(
            {"message": "This account is inactive. Contact an administrator."},
            status=status.HTTP_403_FORBIDDEN,
        )

    return user, None


def _get_admin_user(request):
    user, error_response = _get_authenticated_user(request)

    if error_response:
        return None, error_response

    if user.get("role") != "Admin":
        return None, Response(
            {"message": "Administrator access is required."},
            status=status.HTTP_403_FORBIDDEN,
        )

    return user, None


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    result = register_service(serializer.validated_data)

    if result["success"]:
        verification_url = (
            f"{config('FRONTEND_URL', default='http://localhost:5173').rstrip('/')}/"
            f"?verify_email={result['verification_token']}"
        )
        try:
            send_mail(
                subject="Verify your Support AI account",
                message=(
                    "Verify ownership of this email address to activate your account. "
                    f"This link expires in 24 hours: {verification_url}"
                ),
                from_email=None,
                recipient_list=[result["user"]["email"]],
                fail_silently=False,
            )
        except Exception:
            # Do not leave a customer thinking an inaccessible account was
            # created. A retry can register normally if SMTP is restored.
            users_collection.delete_one({"_id": result["user"]["_id"]})
            return Response(
                {"message": "We could not send the verification email. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response(
            {
                "message": result["message"],
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(
        {"message": result["message"]},
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def verify_email(request):
    token = request.data.get("token")
    if not isinstance(token, str) or not token:
        return Response({"message": "Verification token is required."}, status=status.HTTP_400_BAD_REQUEST)
    result = verify_email_service(token)
    return Response(
        {"message": result["message"]},
        status=status.HTTP_200_OK if result["success"] else status.HTTP_400_BAD_REQUEST,
    )


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def resend_verification_email(request):
    email_serializer = serializers.EmailField()
    try:
        email = email_serializer.run_validation(request.data.get("email", "")).strip()
    except serializers.ValidationError as error:
        return Response({"message": error.detail}, status=status.HTTP_400_BAD_REQUEST)

    token = issue_email_verification(email)
    if token:
        verification_url = (
            f"{config('FRONTEND_URL', default='http://localhost:5173').rstrip('/')}/"
            f"?verify_email={token}"
        )
        try:
            send_mail(
                subject="Verify your Support AI account",
                message=(
                    "Verify ownership of this email address to activate your account. "
                    f"This link expires in 24 hours: {verification_url}"
                ),
                from_email=None,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception:
            return Response(
                {"message": "We could not send the verification email. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

    # Keep this response identical for unknown, already-verified, and ineligible accounts.
    return Response(
        {"message": "If that address has an unverified customer account, a fresh verification link has been sent."},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def login(request):
    

    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():
        debug_user = users_collection.find_one(
            {"email": serializer.validated_data["email"]}
        )

        
    

    
    

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    result = login_service(serializer.validated_data)

    if result["success"]:
        return Response(
            {
                "message": result["message"],
                "access": result["access"],
                "refresh": result["refresh"],
            },
            status=status.HTTP_200_OK,
        )

    return Response(
        {"message": result["message"]},
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def me(request):
    user, error_response = _get_authenticated_user(request)

    if error_response:
        return error_response

    return Response(
        {
            "username": user["username"],
            "email": user["email"],
            "mobile": user.get("mobile", ""),
            "role": user.get("role") or "User",
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET", "POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def admin_users(request):
    admin_user, error_response = _get_admin_user(request)

    if error_response:
        return error_response

    if request.method == "GET":
        users = [
            _normalise_managed_user(user)
            for user in users_collection.find({}, SAFE_USER_PROJECTION).sort("username", 1)
        ]
        return Response(
            {
                "users": ManagedUserSerializer(users, many=True).data,
                "roles": USER_ROLES,
                "categories": list(AGENT_SPECIALTY_CATEGORIES),
            },
            status=status.HTTP_200_OK,
        )

    serializer = ManagedUserCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    result = create_managed_user(serializer.validated_data)
    if not result["success"]:
        return Response(
            {"message": result["message"]},
            status=status.HTTP_400_BAD_REQUEST,
        )

    safe_user = _normalise_managed_user(result["user"])
    return Response(
        {"user": ManagedUserSerializer(safe_user).data},
        status=status.HTTP_201_CREATED,
    )


@api_view(["PATCH"])
@authentication_classes([])
@permission_classes([AllowAny])
def admin_user_detail(request, user_id):
    admin_user, error_response = _get_admin_user(request)

    if error_response:
        return error_response

    try:
        target_user = users_collection.find_one({"_id": ObjectId(user_id)})
    except Exception:
        target_user = None

    if not target_user:
        return Response(
            {"message": "Account not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = ManagedUserUpdateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    result = update_managed_user(
        actor_id=admin_user["_id"],
        target_user=target_user,
        updates=serializer.validated_data,
    )

    if not result["success"]:
        return Response(
            {"message": result["message"]},
            status=result["status_code"],
        )

    safe_user = _normalise_managed_user(result["user"])
    return Response(
        {"user": ManagedUserSerializer(safe_user).data},
        status=status.HTTP_200_OK,
    )
