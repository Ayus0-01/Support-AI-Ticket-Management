from datetime import datetime

from apps.tickets.classification.sla import (
    calculate_sla,
)


print("=" * 70)
print("SLA TEST")
print("=" * 70)


# Monday at 10:00 AM
created_at = datetime(
    2026,
    8,
    17,
    10,
    0
)


for priority in [
    "P1",
    "P2",
    "P3",
    "P4",
]:

    result = calculate_sla(
        priority,
        created_at
    )

    print()
    print(f"Priority: {priority}")

    print(
        "First response:",
        result["first_response_due"]
    )

    print(
        "Resolution:",
        result["resolution_due"]
    )


print()
print("=" * 70)