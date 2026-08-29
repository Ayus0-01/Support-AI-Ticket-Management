from datetime import datetime, timezone
from AIticket.db import (
    tickets_collection,
    agent_workflows_collection,
    agent_executions_collection,
    resolution_feedback_collection,
)

# SLA Target Durations in Hours
SLA_TARGET_HOURS = {
    "P1": 2,
    "P2": 4,
    "P3": 8,
    "P4": 24,
}

def get_analytics_summary():
    """
    Computes ticket volume metrics, AI vs Human resolution rates,
    average resolution latency, AI confidence averages, and CSAT scores.
    """
    tickets = list(tickets_collection.find())
    total_tickets = len(tickets)
    
    status_counts = {"Open": 0, "In Progress": 0, "Resolved": 0, "Closed": 0}
    resolved_tickets_list = []
    
    for t in tickets:
        st = t.get("status", "Open")
        status_counts[st] = status_counts.get(st, 0) + 1
        if st in ("Resolved", "Closed"):
            resolved_tickets_list.append(t)
            
    resolved_tickets_count = len(resolved_tickets_list)

    # Workflows completed
    workflows = list(agent_workflows_collection.find())
    ai_resolved_count = sum(1 for w in workflows if w.get("workflow_status") == "COMPLETED")
    human_resolved_count = max(0, resolved_tickets_count - ai_resolved_count)

    ai_resolution_rate = round((ai_resolved_count / total_tickets * 100) if total_tickets > 0 else 0.0, 2)

    # Resolution Latency Calculation
    latencies = []
    for t in resolved_tickets_list:
        created_at = t.get("created_at")
        updated_at = t.get("updated_at")
        if created_at and updated_at and isinstance(created_at, datetime) and isinstance(updated_at, datetime):
            delta = (updated_at - created_at).total_seconds()
            if delta >= 0:
                latencies.append(delta)
                
    avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else 0.0

    # Average AI Confidence
    confidences = [w["final_confidence"] for w in workflows if w.get("final_confidence") is not None]
    avg_confidence = round(sum(confidences) / len(confidences), 2) if confidences else 0.0

    # Customer Satisfaction Score (CSAT)
    feedbacks = list(resolution_feedback_collection.find())
    feedback_ratings = [f.get("rating") for f in feedbacks if isinstance(f.get("rating"), (int, float))]
    satisfaction_avg = round(sum(feedback_ratings) / len(feedback_ratings), 2) if feedback_ratings else 0.0

    return {
        "total_tickets": total_tickets,
        "open_tickets": status_counts.get("Open", 0),
        "in_progress_tickets": status_counts.get("In Progress", 0),
        "resolved_tickets": status_counts.get("Resolved", 0),
        "closed_tickets": status_counts.get("Closed", 0),
        "ai_resolved_count": ai_resolved_count,
        "human_resolved_count": human_resolved_count,
        "ai_resolution_rate": ai_resolution_rate,
        "avg_resolution_latency_seconds": avg_latency,
        "avg_ai_confidence": avg_confidence,
        "satisfaction_score_avg": satisfaction_avg,
        "total_feedback_count": len(feedbacks),
    }

def get_sla_metrics():
    """
    Evaluates SLA compliance per priority level and calculates overall compliance.
    """
    tickets = list(tickets_collection.find({"status": {"$in": ["Resolved", "Closed"]}}))
    total_evaluated = len(tickets)

    priority_stats = {
        "P1": {"met": 0, "breached": 0, "target_hours": 2},
        "P2": {"met": 0, "breached": 0, "target_hours": 4},
        "P3": {"met": 0, "breached": 0, "target_hours": 8},
        "P4": {"met": 0, "breached": 0, "target_hours": 24},
    }

    met_total = 0
    breached_total = 0

    for t in tickets:
        priority = t.get("priority", "P3")
        if priority not in priority_stats:
            priority = "P3"

        created_at = t.get("created_at")
        updated_at = t.get("updated_at")
        target_hours = SLA_TARGET_HOURS.get(priority, 8)

        if created_at and updated_at and isinstance(created_at, datetime) and isinstance(updated_at, datetime):
            elapsed_hours = (updated_at - created_at).total_seconds() / 3600.0
            if elapsed_hours <= target_hours:
                priority_stats[priority]["met"] += 1
                met_total += 1
            else:
                priority_stats[priority]["breached"] += 1
                breached_total += 1
        else:
            # Default to met if timestamps missing in legacy data
            priority_stats[priority]["met"] += 1
            met_total += 1

    overall_compliance = round((met_total / total_evaluated * 100) if total_evaluated > 0 else 100.0, 2)

    return {
        "overall_compliance_rate": overall_compliance,
        "total_evaluated_tickets": total_evaluated,
        "met_sla_count": met_total,
        "breached_sla_count": breached_total,
        "sla_by_priority": priority_stats,
    }

def get_agent_performance_metrics():
    """
    Calculates execution counts, workflow states, and average execution time for each AI agent step.
    """
    executions = list(agent_executions_collection.find())
    workflows = list(agent_workflows_collection.find())

    execution_by_agent = {}
    durations_by_agent = {}

    for ex in executions:
        agent_name = ex.get("agent_name", "Unknown Agent")
        execution_by_agent[agent_name] = execution_by_agent.get(agent_name, 0) + 1

        start = ex.get("started_at")
        end = ex.get("completed_at")
        if start and end and isinstance(start, datetime) and isinstance(end, datetime):
            ms = (end - start).total_seconds() * 1000.0
            durations_by_agent.setdefault(agent_name, []).append(ms)

    avg_durations = {}
    for agent_name, d_list in durations_by_agent.items():
        avg_durations[agent_name] = round(sum(d_list) / len(d_list), 2) if d_list else 0.0

    completion_breakdown = {"COMPLETED": 0, "ESCALATED": 0, "RUNNING": 0, "FAILED": 0}
    for w in workflows:
        st = w.get("workflow_status", "RUNNING")
        completion_breakdown[st] = completion_breakdown.get(st, 0) + 1

    return {
        "total_agent_executions": len(executions),
        "execution_by_agent_name": execution_by_agent,
        "workflow_completion_breakdown": completion_breakdown,
        "avg_step_duration_ms": avg_durations,
    }
