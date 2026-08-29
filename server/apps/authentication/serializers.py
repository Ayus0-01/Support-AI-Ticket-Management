from rest_framework import serializers


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


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True
    )


class AdminUserResponseSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    mobile = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    def get_id(self, obj):
        if isinstance(obj, dict):
            return str(obj.get("_id", ""))
        return str(getattr(obj, "_id", getattr(obj, "id", "")))

    def get_username(self, obj):
        if isinstance(obj, dict):
            return obj.get("username") or ""
        return getattr(obj, "username", "") or ""

    def get_email(self, obj):
        if isinstance(obj, dict):
            return obj.get("email") or ""
        return getattr(obj, "email", "") or ""

    def get_mobile(self, obj):
        if isinstance(obj, dict):
            return obj.get("mobile") or ""
        return getattr(obj, "mobile", "") or ""

    def get_role(self, obj):
        if isinstance(obj, dict):
            return obj.get("role") or "User"
        return getattr(obj, "role", "User") or "User"

    def get_status(self, obj):
        if isinstance(obj, dict):
            return obj.get("status") or "Active"
        return getattr(obj, "status", "Active") or "Active"



class AdminCreateUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    mobile = serializers.CharField(required=False, allow_blank=True, default="")
    password = serializers.CharField(min_length=8, write_only=True)
    role = serializers.ChoiceField(choices=["User", "Agent", "Admin"], default="User")
    status = serializers.ChoiceField(choices=["Active", "Inactive"], default="Active")


class AdminUpdateUserSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=["User", "Agent", "Admin"], required=False)
    status = serializers.ChoiceField(choices=["Active", "Inactive"], required=False)