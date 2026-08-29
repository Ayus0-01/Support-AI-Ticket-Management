from rest_framework import serializers

class AnalyticsSummarySerializer(serializers.Serializer):
    total_tickets = serializers.IntegerField()
    open_tickets = serializers.IntegerField()
    in_progress_tickets = serializers.IntegerField()
    resolved_tickets = serializers.IntegerField()
    closed_tickets = serializers.IntegerField()
    ai_resolved_count = serializers.IntegerField()
    human_resolved_count = serializers.IntegerField()
    ai_resolution_rate = serializers.FloatField()
    avg_resolution_latency_seconds = serializers.FloatField()
    avg_ai_confidence = serializers.FloatField()
    satisfaction_score_avg = serializers.FloatField()
    total_feedback_count = serializers.IntegerField()

class SLAMetricsSerializer(serializers.Serializer):
    overall_compliance_rate = serializers.FloatField()
    total_evaluated_tickets = serializers.IntegerField()
    met_sla_count = serializers.IntegerField()
    breached_sla_count = serializers.IntegerField()
    sla_by_priority = serializers.DictField()

class AgentPerformanceSerializer(serializers.Serializer):
    total_agent_executions = serializers.IntegerField()
    execution_by_agent_name = serializers.DictField()
    workflow_completion_breakdown = serializers.DictField()
    avg_step_duration_ms = serializers.DictField()
