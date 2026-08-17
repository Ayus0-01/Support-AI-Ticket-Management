from datetime import datetime, timezone


def get_ticket_sla_due_at(ticket):
    """
    Get the active SLA deadline from a real ticket.

    Open/In Progress tickets use the first-response SLA.
    Resolution SLA is used as a fallback.
    """

    sla = ticket.get("sla")

    if isinstance(sla, dict):

        due_at = sla.get(
            "first_response_due"
        )

        if not due_at:
            due_at = sla.get(
                "resolution_due"
            )

    else:
        due_at = ticket.get(
            "sla_due_at"
        )

    if not due_at:
        return None

    if isinstance(due_at, str):
        due_at = datetime.fromisoformat(
            due_at.replace(
                "Z",
                "+00:00"
            )
        )

    if due_at.tzinfo is None:
        due_at = due_at.replace(
            tzinfo=timezone.utc
        )

    return due_at


def get_sla_seconds(ticket):
    """
    Return seconds remaining until the
    active SLA deadline.
    """

    due_at = get_ticket_sla_due_at(
        ticket
    )

    if due_at is None:
        return float("inf")

    now = datetime.now(
        timezone.utc
    )

    return (
        due_at - now
    ).total_seconds()


def sort_ticket_queue(tickets):
    """
    Sort tickets by time remaining
    until the active SLA deadline.

    Earliest SLA breach appears first.
    """

    return sorted(
        tickets,
        key=get_sla_seconds
    )