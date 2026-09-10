from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .constants import USER_ROLES


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    mobile = serializers.CharField(
        required=False,
        allow_blank=True
    )
    password = serializers.CharField(
        min_length=8,
        write_only=True
    )

    def validate_password(self, value):
        validate_password(value)
        return value


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True
    )


class ManagedUserSerializer(serializers.Serializer):
    """Whitelist the account fields that are safe for administration."""

    id = serializers.SerializerMethodField()
    username = serializers.CharField()
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=USER_ROLES)
    is_active = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(allow_null=True, required=False)
    last_login_at = serializers.DateTimeField(allow_null=True, required=False)

    def get_id(self, obj):
        return str(obj["_id"])

    def get_is_active(self, obj):
        return obj.get("is_active", True)


class ManagedUserCreateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100, trim_whitespace=True)
    email = serializers.EmailField()
    mobile = serializers.CharField(required=False, allow_blank=True, max_length=30)
    password = serializers.CharField(min_length=8, write_only=True)
    role = serializers.ChoiceField(choices=USER_ROLES)

    def validate_password(self, value):
        validate_password(value)
        return value


class ManagedUserUpdateSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=USER_ROLES, required=False)
    is_active = serializers.BooleanField(required=False)

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError(
                "Provide a role or account status to update."
            )
        return attrs
