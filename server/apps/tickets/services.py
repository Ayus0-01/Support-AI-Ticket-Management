from datetime import datetime, timezone
from uuid import uuid4

from AIticket.db import tickets_collection
from bson import ObjectId


def create_ticket(data, requester):
    ticket_id = (
        f"IT-{datetime.now(timezone.utc).year}-"
        f"{uuid4().hex[:6].upper()}"
    )

    now = datetime.now(timezone.utc)

    ticket = {
        "ticket_id": ticket_id,

        # Requester information
        "requester": {
            "user_id": requester.get("user_id"),
            "username": requester.get("username"),
            "email": requester.get("email"),
        },

        # Information provided by the user
        "subject": data["subject"],
        "category": data["category"],
        "description": data["description"],
        "department": data.get("department", ""),
        "site": data.get("site", ""),
        "asset_tag": data.get("asset_tag", ""),
        "preferred_contact": data.get("preferred_contact", ""),

        # System-managed fields
        "status": "Open",
        "priority": None,
        "severity": None,
        "subcategory": None,
        "confidence": None,
        "path": None,
        "sla": None,
        "assignee": None,

        # Timestamps
        "created_at": now,
        "updated_at": now,
    }

    result = tickets_collection.insert_one(ticket)

    # Convert MongoDB ObjectId to string
    ticket["_id"] = str(result.inserted_id)

    return ticket


def get_user_tickets(user_id):
    """
    Get all tickets created by a specific user.
    """

    tickets = tickets_collection.find(
        {
            "requester.user_id": str(user_id)
        }
    ).sort("created_at", -1)

    result = []

    for ticket in tickets:
        ticket["_id"] = str(ticket["_id"])
        result.append(ticket)

    return result


def get_ticket_by_id(ticket_id, user_id):
    """
    Get one ticket belonging to a specific user.
    """

    ticket = tickets_collection.find_one(
        {
            "ticket_id": ticket_id,
            "requester.user_id": str(user_id)
        }
    )

    if not ticket:
        return None

    ticket["_id"] = str(ticket["_id"])

    return ticket