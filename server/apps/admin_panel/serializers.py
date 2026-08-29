from rest_framework import serializers

class SystemOverviewSerializer(serializers.Serializer):
    status = serializers.CharField()
    timestamp = serializers.DateTimeField()
    database_status = serializers.CharField()
    collections_count = serializers.DictField()
    vector_indices_count = serializers.IntegerField()
    active_agent_workflows = serializers.IntegerField()
    ollama_model_status = serializers.CharField()

class SystemStatusSerializer(serializers.Serializer):
    status = serializers.CharField()
    uptime_status = serializers.CharField()
    version = serializers.CharField()
