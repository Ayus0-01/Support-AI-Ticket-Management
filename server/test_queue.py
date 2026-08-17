from datetime import datetime, timedelta, timezone

from apps.tickets.queue import sort_ticket_queue


now = datetime.now(timezone.utc)


tickets = [
    {
        "ticket_number": "IT-004",
        "priority": "P4",
        "sla_due_at": (
            now + timedelta(hours=20)
        ).isoformat(),
    },
    {
        "ticket_number": "IT-001",
        "priority": "P1",
        "sla_due_at": (
            now + timedelta(minutes=10)
        ).isoformat(),
    },
    {
        "ticket_number": "IT-003",
        "priority": "P3",
        "sla_due_at": (
            now + timedelta(hours=4)
        ).isoformat(),
    },
    {
        "ticket_number": "IT-002",
        "priority": "P2",
        "sla_due_at": (
            now + timedelta(hours=1)
        ).isoformat(),
    },
]


print("=" * 70)
print("QUEUE ORDER TEST")
print("=" * 70)


sorted_tickets = sort_ticket_queue(tickets)


for position, ticket in enumerate(
    sorted_tickets,
    start=1
):

    print(
        f"{position}. "
        f"{ticket['ticket_number']} | "
        f"{ticket['priority']} | "
        f"{ticket['sla_due_at']}"
    )


expected_order = [
    "IT-001",
    "IT-002",
    "IT-003",
    "IT-004",
]


actual_order = [
    ticket["ticket_number"]
    for ticket in sorted_tickets
]


assert actual_order == expected_order


print("\nQueue ordering test passed.")