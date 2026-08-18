from rest_framework import serializers

class CreateTicketSerializer(serializers.Serializer):
    subject = serializers.CharField(
        max_length=255
    )

    category = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True
    )

    description = serializers.CharField()

    department = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True
    )

    site = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True
    )

    asset_tag = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True
    )

    preferred_contact = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True
    )
    affected_scope = serializers.ChoiceField(
        choices=[
            ("JUST_ME", "Just me"),
            ("TEAM", "My team"),
            ("DEPARTMENT", "My department"),
            ("ORGANISATION", "Whole organisation"),
        ],
        required=True,
    )

    work_blocked = serializers.ChoiceField(
        choices=[
            ("YES", "Yes"),
            ("PARTIALLY", "Partially"),
            ("NO", "No"),
        ],
        required=True,
    )

    urgent_feeling = serializers.ChoiceField(
        choices=[
            ("LOW", "Low"),
            ("MEDIUM", "Medium"),
            ("HIGH", "High"),
        ],
        required=False,
        default="LOW",
    )

    workaround_available = serializers.BooleanField(
        required=False,
        default=False,
    )

class CheckDuplicateSerializer(serializers.Serializer):
    subject = serializers.CharField(
        max_length=255
    )

    description = serializers.CharField()

class PreviewClassifySerializer(serializers.Serializer):
    subject = serializers.CharField(
        max_length=255
    )

    description = serializers.CharField()

class EmployeeTicketSerializer(serializers.Serializer):
    
    ticket_id = serializers.CharField()

    subject = serializers.CharField()

    description = serializers.CharField()

    department = serializers.CharField(
        allow_blank=True,
        required=False,
    )

    site = serializers.CharField(
        allow_blank=True,
        required=False,
    )

    asset_tag = serializers.CharField(
        allow_blank=True,
        required=False,
    )

    preferred_contact = serializers.CharField(
        allow_blank=True,
        required=False,
    )

    status = serializers.CharField()

    resolution = serializers.SerializerMethodField()

    def get_resolution(self, obj):
        resolution = obj.get(
            "resolution"
        )

        if not resolution:
            return None

        return {
            "summary": resolution.get(
                "summary"
            ),
            "resolved_at": resolution.get(
                "resolved_at"
            ),
    }    

    severity = serializers.CharField(
        allow_null=True,
        required=False,
    )

    priority = serializers.SerializerMethodField()

    sla = serializers.DictField(
        allow_null=True,
        required=False,
    )

    queue = serializers.CharField(
        allow_null=True,
        required=False,
    )

    created_at = serializers.DateTimeField(
        allow_null=True,
        required=False,
    )

    updated_at = serializers.DateTimeField(
        allow_null=True,
        required=False,
    )
    def get_priority(self, obj):
        priority = obj.get("priority")

        if isinstance(priority, dict):
            return priority.get(
                "value"
        )

        return priority

class ClassificationOverrideSerializer(serializers.Serializer):
    category = serializers.CharField(
        max_length=100,
        required=False,
    )

    severity = serializers.ChoiceField(
        choices=[
            ("LOW", "Low"),
            ("MEDIUM", "Medium"),
            ("HIGH", "High"),
            ("CRITICAL", "Critical"),
        ],
        required=False,
    )

class StatusTransitionSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[
            ("Open", "Open"),
            ("In Progress", "In Progress"),
            ("Resolved", "Resolved"),
        ],
        required=True,
    )

    resolution_summary = serializers.CharField(
        max_length=5000,
        required=False,
        allow_blank=True,
    )

    def validate(self, attrs):
        status_value = attrs.get(
            "status"
        )

        resolution_summary = (
            attrs.get(
                "resolution_summary",
                ""
            )
        ).strip()

        if (
            status_value == "Resolved"
            and not resolution_summary
        ):
            raise serializers.ValidationError(
                {
                    "resolution_summary":
                        "Resolution summary is required "
                        "when resolving a ticket."
                }
            )

        return attrs

class TicketCommentSerializer(serializers.Serializer):
    comment = serializers.CharField(
        max_length=5000,
        required=True,
    )

    visibility = serializers.ChoiceField(
        choices=[
            ("PUBLIC", "Public"),
            ("INTERNAL", "Internal"),
        ],
        required=True,
    )

