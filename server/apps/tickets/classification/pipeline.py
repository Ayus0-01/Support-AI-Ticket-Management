from .category_classifier import predict_category
from .subcategory_classifier import predict_subcategory
from .severity_prediction import predict_severity
from .severity_rules import apply_severity_overrides
from .priority import (
    calculate_priority,
    explain_priority,
)
from .sla import calculate_sla
from .routing import route_ticket
import time


def classify_ticket(
    subject,
    description,
    affected_scope="JUST_ME",
    work_blocked="NO",
    urgent_feeling="LOW",
    workaround_available=False,
    channel="",
    is_vip=False,
    similar_tickets_last_hour=0,
    created_at=None,
):
    pipeline_start = time.perf_counter()
    """
    Run the complete ticket classification pipeline.

    Pipeline:

        Category
        ↓
        Subcategory
        ↓
        Severity
        ↓
        Severity rules
        ↓
        Priority
        ↓
        SLA
        ↓
        Queue
    """

    category_result = predict_category(
        subject=subject,
        description=description,
        channel=channel,
    )

    category = category_result["category"]


    subcategory_result = predict_subcategory(
        subject=subject,
        description=description,
    )

    subcategory = (
        subcategory_result["subcategory"]
    )

    severity_result = predict_severity(
        affected_scope=affected_scope,
        work_blocked=work_blocked,
        urgent_feeling=urgent_feeling,
        workaround_available=workaround_available,
        category=category,
    )

    severity = severity_result["severity"]



    severity_override = apply_severity_overrides(
        severity=severity,
        category=category,
        affected_scope=affected_scope,
        is_vip=is_vip,
        subject=subject,
        description=description,
        similar_tickets_last_hour=similar_tickets_last_hour,
    )

    final_severity = severity_override[
        "severity"
    ]

    rules_fired = severity_override[
        "rules_fired"
    ]


    priority = calculate_priority(
        severity=final_severity,
        affected_scope=affected_scope,
    )

    priority_reason = explain_priority(
        severity=final_severity,
        affected_scope=affected_scope,
        priority=priority,
    )

    sla = calculate_sla(
        priority=priority,
        created_at=created_at,
    )


    queue = route_ticket(
        category=category
    )

    latency_ms = round(
    (
        time.perf_counter()
        - pipeline_start
    ) * 1000,
    2,
)

    return {
        "category": {
            "value": category,
            "confidence": category_result[
                "confidence"
            ],
            "route": category_result[
                "route"
            ],
        },

        "subcategory": {
            "value": subcategory,
            "confidence": subcategory_result[
                "confidence"
            ],
            "route": subcategory_result[
                "route"
            ],
        },

        "severity": {
            "value": final_severity,
            "model_prediction": severity,
            "confidence": severity_result[
                "confidence"
            ],
            "rules_fired": rules_fired,
        },

        "priority": { 
            "value": priority,
            "reason": priority_reason,
        },

        "sla": sla,

        "queue": queue,

        "model_metadata": {
          "category_model_version": "category-v1",
          "subcategory_model_version": "subcategory-v1",
          "severity_model_version": "severity-v1",
          "pipeline_latency_ms": latency_ms,
        },
    }