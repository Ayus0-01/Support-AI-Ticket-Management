from datetime import datetime

from .pipeline import classify_ticket


print("=" * 100)
print("UNIFIED TICKET CLASSIFICATION TEST")
print("=" * 100)


result = classify_ticket(
    subject="VPN connection failing",

    description=(
        "I cannot connect to the company VPN "
        "and I am unable to access internal systems."
    ),

    affected_scope="TEAM",

    work_blocked="YES",

    urgent_feeling="HIGH",

    workaround_available=False,

    channel="portal",

    is_vip=False,

    similar_tickets_last_hour=0,

    created_at=datetime(
        2026,
        8,
        17,
        10,
        0,
    ),
)


print("\nCATEGORY")
print("-" * 50)
print(result["category"])


print("\nSUBCATEGORY")
print("-" * 50)
print(result["subcategory"])


print("\nSEVERITY")
print("-" * 50)
print(result["severity"])


print("\nPRIORITY")
print("-" * 50)
print(result["priority"])


print("\nPRIORITY REASON")
print("-" * 50)
print(result["priority"]["reason"])


print("\nSLA")
print("-" * 50)
print(result["sla"])


print("\nQUEUE")
print("-" * 50)
print(result["queue"])


print("\nMODEL METADATA")
print("-" * 50)
print(result["model_metadata"])


print("\n" + "=" * 100)
print("PIPELINE COMPLETE")
print("=" * 100)