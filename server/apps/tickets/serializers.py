from rest_framework import serializers

class CreateTicketSerializer(serializers.Serializer):
    subject = serializers.CharField(
        max_length=255
    )

    category = serializers.CharField(
        max_length=100
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