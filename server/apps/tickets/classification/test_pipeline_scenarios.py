from datetime import datetime

from .pipeline import classify_ticket


TESTS = [

    {
        "name": "LOW - Individual inconvenience",
        "subject": "Minor software inconvenience",
        "description": "The application is slightly inconvenient but I can continue working.",
        "affected_scope": "JUST_ME",
        "work_blocked": "NO",
        "urgent_feeling": "LOW",
        "workaround_available": True,
        "channel": "portal",
    },

    {
        "name": "MEDIUM - Team disruption",
        "subject": "Team VPN degradation",
        "description": "Several team members are experiencing slower VPN access but can still work.",
        "affected_scope": "TEAM",
        "work_blocked": "PARTIALLY",
        "urgent_feeling": "MEDIUM",
        "workaround_available": True,
        "channel": "portal",
    },

    {
        "name": "HIGH - Department outage",
        "subject": "Department network outage",
        "description": "The department network is unavailable and employees cannot access internal systems.",
        "affected_scope": "DEPARTMENT",
        "work_blocked": "YES",
        "urgent_feeling": "HIGH",
        "workaround_available": False,
        "channel": "portal",
    },

    {
        "name": "CRITICAL - Organisation outage",
        "subject": "Organisation network outage",
        "description": "The entire organisation is unable to access the corporate network.",
        "affected_scope": "ORGANISATION",
        "work_blocked": "YES",
        "urgent_feeling": "HIGH",
        "workaround_available": False,
        "channel": "portal",
    },

    {
        "name": "SECURITY - Suspicious login",
        "subject": "Suspicious login detected",
        "description": "A suspicious login was detected and the user's credentials may have been compromised.",
        "affected_scope": "JUST_ME",
        "work_blocked": "YES",
        "urgent_feeling": "HIGH",
        "workaround_available": False,
        "channel": "portal",
    },

    {
        "name": "VIP - Individual issue",
        "subject": "Executive laptop problem",
        "description": "My laptop application is not working correctly.",
        "affected_scope": "JUST_ME",
        "work_blocked": "PARTIALLY",
        "urgent_feeling": "LOW",
        "workaround_available": True,
        "channel": "portal",
        "is_vip": True,
    },

    {
        "name": "EMERGING INCIDENT",
        "subject": "Network problem",
        "description": "Multiple users are reporting the same network problem.",
        "affected_scope": "TEAM",
        "work_blocked": "PARTIALLY",
        "urgent_feeling": "MEDIUM",
        "workaround_available": True,
        "channel": "portal",
        "similar_tickets_last_hour": 10,
    },
]


print("=" * 100)
print("MULTI-SCENARIO TICKET PIPELINE TEST")
print("=" * 100)


for number, test in enumerate(TESTS, start=1):

    test_data = test.copy()

    name = test_data.pop("name")

    test_data.setdefault("is_vip", False)
    test_data.setdefault("similar_tickets_last_hour", 0)

    test_data["created_at"] = datetime(
        2026,
        8,
        17,
        10,
        0,
    )

    result = classify_ticket(**test_data)

    print()
    print("=" * 100)
    print(f"TEST {number}: {name}")
    print("=" * 100)

    print(
        "Category:",
        result["category"]
    )

    print(
        "Subcategory:",
        result["subcategory"]
    )

    print(
        "Severity:",
        result["severity"]
    )

    print(
        "Priority:",
        result["priority"]
    )

    print(
        "SLA:",
        result["sla"]
    )

    print(
        "Queue:",
        result["queue"]
    )


print()
print("=" * 100)
print("MULTI-SCENARIO TEST COMPLETE")
print("=" * 100)