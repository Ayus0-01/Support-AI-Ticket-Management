from rest_framework import serializers

class AuditEventSerializer(serializers.Serializer):
    id = serializers.CharField(source="_id", read_only=True)
    user_id = serializers.CharField(allow_null=True, required=False)
    username = serializers.CharField(allow_null=True, required=False)
    action_type = serializers.CharField()
    target_type = serializers.CharField()
    target_id = serializers.CharField(allow_null=True, required=False)
    details = serializers.DictField(required=False)
    ip_address = serializers.CharField(allow_null=True, required=False)
    timestamp = serializers.DateTimeField()

class TicketHistoryEventSerializer(serializers.Serializer):
    event_type = serializers.CharField()
    timestamp = serializers.DateTimeField()
    performed_by = serializers.CharField(allow_null=True, required=False)
    details = serializers.DictField()
