from rest_framework import serializers

class WorkflowStartSerializer(serializers.Serializer):
    ticket_id = serializers.CharField(required=True)

class AgentExecutionSerializer(serializers.Serializer):
    id = serializers.CharField(source="_id", read_only=True)
    workflow_id = serializers.CharField()
    agent_name = serializers.CharField()
    input_data = serializers.DictField(required=False)
    output_data = serializers.DictField(required=False)
    status = serializers.CharField()
    confidence = serializers.FloatField(required=False)
    started_at = serializers.DateTimeField(required=False)
    completed_at = serializers.DateTimeField(required=False)

class WorkflowStatusSerializer(serializers.Serializer):
    id = serializers.CharField(source="_id", read_only=True)
    ticket_id = serializers.CharField()
    workflow_status = serializers.CharField()
    current_agent = serializers.CharField()
    final_confidence = serializers.FloatField(allow_null=True, required=False)
    started_at = serializers.DateTimeField(required=False)
    completed_at = serializers.DateTimeField(allow_null=True, required=False)

class JiraTicketSerializer(serializers.Serializer):
    id = serializers.CharField(source="_id", read_only=True)
    ticket_id = serializers.CharField()
    jira_issue_key = serializers.CharField()
    jira_status = serializers.CharField()
    last_updated = serializers.DateTimeField(required=False)

class EmailLogSerializer(serializers.Serializer):
    id = serializers.CharField(source="_id", read_only=True)
    ticket_id = serializers.CharField()
    recipient = serializers.EmailField()
    subject = serializers.CharField()
    email_type = serializers.CharField()
    status = serializers.CharField()
    sent_at = serializers.DateTimeField(required=False)
