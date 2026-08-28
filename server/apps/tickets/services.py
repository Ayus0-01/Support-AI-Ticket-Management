from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from pymongo import ReturnDocument
import threading
import re
import math

from AIticket.db import (
    tickets_collection, 
    counters_collection, 
    classification_overrides_collection, 
    status_history_collection,
    comments_collection,
)
from .classification.embeddings import generate_embedding


IST = ZoneInfo("Asia/Kolkata")


def get_next_ticket_number():
    result = counters_collection.find_one_and_update(
        {"_id": "tickets"},
        {"$inc": {"sequence": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )

    return result["sequence"]


def create_ticket(data, requester):
    sequence = get_next_ticket_number()

    current_year = datetime.now(timezone.utc).year

    ticket_id = f"IT-{current_year}-{sequence:06d}"

    now = datetime.now(timezone.utc)

    ticket = {
    "ticket_id": ticket_id,

    "requester": {
        "user_id": requester.get("user_id"),
        "username": requester.get("username"),
        "email": requester.get("email"),
    },

    "subject": data["subject"],
    "description": data["description"],

    "affected_system": data.get(
        "affected_system",
        "",
    ),

    "department": data.get(
        "department",
        "",
    ),

    "site": data.get(
        "site",
        "",
    ),

    "asset_tag": data.get(
        "asset_tag",
        "",
    ),

    "preferred_contact": data.get(
        "preferred_contact",
        "",
    ),

    # Step 4 — Impact
    "affected_scope": data.get(
        "affected_scope",
        "JUST_ME",
    ),

    "work_blocked": data.get(
        "work_blocked",
        "NO",
    ),

    "urgent_feeling": data.get(
        "urgent_feeling",
        "LOW",
    ),

    "workaround_available": data.get(
        "workaround_available",
        False,
    ),

    "channel": data.get(
        "channel",
        "portal",
    ),

    "status": "Open",
    "category": None,
    "resolution": None,
    "subcategory": None,
    "severity": None,
    "priority": None,
    "sla": None,
    "queue": None,

    "classification": None,

    "assignee": None,

    "created_at": now,
    "updated_at": now,
}

    result = tickets_collection.insert_one(ticket)

    ticket["_id"] = str(result.inserted_id)

    return ticket

def classify_and_update_ticket(ticket_id):
    """
    Run the complete classification pipeline for an
    already-created ticket and persist the result.
    """

    from .classification.pipeline import classify_ticket

    ticket = tickets_collection.find_one(
        {
            "ticket_id": ticket_id
        }
    )

    if not ticket:
        return None

    result = classify_ticket(
        subject=ticket["subject"],
        description=ticket["description"],
        affected_scope=ticket.get(
            "affected_scope",
            "JUST_ME",
        ),
        work_blocked=ticket.get(
            "work_blocked",
            "NO",
        ),
        urgent_feeling=ticket.get(
            "urgent_feeling",
            "LOW",
        ),
        workaround_available=ticket.get(
            "workaround_available",
            False,
        ),
        channel=ticket.get(
            "channel",
            "portal",
        ),
        created_at=ticket.get(
            "created_at"
        ),
    )

    tickets_collection.update_one(
        {
            "ticket_id": ticket_id
        },
        {
            "$set": {
                "category": result["category"]["value"],
                "subcategory": result["subcategory"]["value"],
                "severity": result["severity"]["value"],
                "priority": result["priority"],
                "sla": result["sla"],
                "queue": result["queue"],
                "classification": result,
                "updated_at": datetime.now(
                    timezone.utc
                ),
            }
        },
    )

    return result

def enqueue_classification(ticket_id):
    """
    Start classification after ticket creation without
    blocking the HTTP response.
    """

    thread = threading.Thread(
        target=classify_and_update_ticket,
        args=(ticket_id,),
        daemon=True,
    )

    thread.start()


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


def normalize_text(text):
    """
    Convert text into normalized lowercase tokens.
    """

    text = text.lower()

    # Keep only letters and numbers
    tokens = re.findall(r"\b[a-z0-9]+\b", text)

    return set(tokens)


def token_overlap_score(text1, text2):
    """
    Calculate Jaccard token similarity between two texts.
    """

    tokens1 = normalize_text(text1)
    tokens2 = normalize_text(text2)

    if not tokens1 or not tokens2:
        return 0.0

    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)

    return len(intersection) / len(union)


def cosine_similarity(vector1, vector2):
    """
    Calculate cosine similarity between two embedding vectors.
    """

    dot_product = sum(
        a * b
        for a, b in zip(vector1, vector2)
    )

    magnitude1 = math.sqrt(
        sum(
            value * value
            for value in vector1
        )
    )

    magnitude2 = math.sqrt(
        sum(
            value * value
            for value in vector2
        )
    )

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    return dot_product / (
        magnitude1 * magnitude2
    )


def check_duplicate_tickets(
    user_id,
    subject,
    description,
):
    """
    Find similar open tickets created by the
    same user within the last 7 days.

    Similarity uses:
        60% embedding similarity
        40% token overlap

    A combined score above 0.80 is treated
    as a duplicate candidate.
    """

    now = datetime.now(
        timezone.utc
    )

    seven_days_ago = (
        now - timedelta(days=7)
    )

    tickets = tickets_collection.find(
        {
            "requester.user_id": str(
                user_id
            ),

            "status": {
                "$in": [
                    "Open",
                    "In Progress",
                ]
            },

            "created_at": {
                "$gte": seven_days_ago
            }
        }
    ).sort(
        "created_at",
        -1
    )

    new_text = (
        f"{subject or ''} "
        f"{description or ''}"
    )

    new_embedding = generate_embedding(
        subject or "",
        description or "",
    )

    duplicates = []

    for ticket in tickets:

        existing_subject = (
            ticket.get(
                "subject",
                ""
            )
        )

        existing_description = (
            ticket.get(
                "description",
                ""
            )
        )

        existing_text = (
            f"{existing_subject} "
            f"{existing_description}"
        )

        existing_embedding = generate_embedding(
            existing_subject,
            existing_description,
        )

        embedding_score = cosine_similarity(
            new_embedding,
            existing_embedding,
        )

        token_score = token_overlap_score(
            new_text,
            existing_text,
        )

        combined_score = (
            0.60 * embedding_score
            +
            0.40 * token_score
        )

        if combined_score > 0.80:

            duplicates.append({
                "ticket_id": ticket.get(
                    "ticket_id"
                ),

                "subject": ticket.get(
                    "subject"
                ),

                "status": ticket.get(
                    "status"
                ),

                "created_at": ticket.get(
                    "created_at"
                ),

                "embedding_score": round(
                    embedding_score,
                    4
                ),

                "token_overlap_score": round(
                    token_score,
                    4
                ),

                "score": round(
                    combined_score,
                    4
                ),
            })

    return duplicates

def get_agent_queue():
    """
    Get tickets that are currently active and
    order them by time remaining to SLA breach.
    """

    from .queue import sort_ticket_queue

    tickets = list(
        tickets_collection.find(
            {
                "status": {
                    "$in": [
                        "Open",
                        "In Progress",
                    ]
                }
            }
        )
    )

    sorted_tickets = sort_ticket_queue(
        tickets
    )

    for ticket in sorted_tickets:
        ticket["_id"] = str(
            ticket["_id"]
        )

    return sorted_tickets

def save_classification_override(
    ticket_id,
    agent_user_id,
    corrected_category,
    corrected_severity,
):
    """
    Store an agent correction as a training-data example.

    The exact subject and description are snapshotted
    from the ticket at the time of correction.
    """

    ticket = tickets_collection.find_one(
        {
            "ticket_id": ticket_id
        }
    )

    if not ticket:
        return None

    classification = (
        ticket.get(
            "classification"
        )
        or {}
    )

    category_result = (
        classification.get(
            "category"
        )
        or {}
    )

    severity_result = (
        classification.get(
            "severity"
        )
        or {}
    )

    override_document = {
        "ticket_id": ticket_id,

        "predicted": {
            "category": category_result.get(
                "value"
            ),

            "severity": severity_result.get(
                "value"
            ),

            "confidence": category_result.get(
                "confidence"
            ),

            "category_confidence": category_result.get(
                "confidence"
            ),

            "severity_confidence": severity_result.get(
                "confidence"
            ),
        },

        "corrected": {
            "category": corrected_category,
            "severity": corrected_severity,
        },

        "subject_snapshot": ticket.get(
            "subject",
            ""
        ),

        "description_snapshot": ticket.get(
            "description",
            ""
        ),

        "agent_user_id": str(
            agent_user_id
        ),

        "created_at": datetime.now(
            timezone.utc
        ),
    }

    result = (
        classification_overrides_collection.insert_one(
            override_document
        )
    )

    override_document["_id"] = str(
        result.inserted_id
    )

    return override_document

def apply_classification_override(
    ticket_id,
    corrected_category=None,
    corrected_severity=None,
):
    """
    Apply an agent's corrected classification to the ticket.

    Only supplied fields are changed.
    Priority and SLA are recalculated after severity changes.
    """
    from .classification.priority import calculate_priority
    from .classification.sla import calculate_sla
    from .classification.routing import route_ticket


    ticket = tickets_collection.find_one(
        {
            "ticket_id": ticket_id
        }
    )

    if not ticket:
        return None

    current_category = ticket.get(
        "category"
    )

    current_severity = ticket.get(
        "severity"
    )

    final_category = (
        corrected_category
        if corrected_category is not None
        else current_category
    )

    final_severity = (
        corrected_severity
        if corrected_severity is not None
        else current_severity
    )

    priority = calculate_priority(
        severity=final_severity,
        affected_scope=ticket.get(
            "affected_scope",
            "JUST_ME",
        ),
    )

    sla = calculate_sla(
        priority=priority,
        created_at=ticket.get(
            "created_at"
        ),
    )

    queue = route_ticket(
        category=final_category
    )

    update_fields = {
        "category": final_category,
        "severity": final_severity,
        "priority": priority,
        "sla": sla,
        "queue": queue,
        "updated_at": datetime.now(
            timezone.utc
        ),
    }

    tickets_collection.update_one(
        {
            "ticket_id": ticket_id
        },
        {
            "$set": update_fields
        },
    )

    return update_fields

VALID_STATUS_TRANSITIONS = {
    "Open": {
        "In Progress",
    },

    "In Progress": {
        "Resolved",
    },

    "Resolved": set(),
}

def transition_ticket_status(
    ticket_id,
    new_status,
    actor_user_id,
    resolution_summary=None,
):
    """
    Change ticket status only when the requested
    transition is explicitly allowed.

    Every valid transition is recorded in
    the status_history collection.
    """

    ticket = tickets_collection.find_one(
        {
            "ticket_id": ticket_id
        }
    )

    if not ticket:
        return {
            "success": False,
            "error": "TICKET_NOT_FOUND",
        }

    current_status = ticket.get(
        "status",
        "Open",
    )

    new_status = (
        new_status or ""
    ).strip()

    resolution_summary = (
        resolution_summary or ""
    ).strip()

    allowed_statuses = (
        VALID_STATUS_TRANSITIONS.get(
            current_status,
            set(),
        )
    )

    if new_status not in allowed_statuses:
        return {
            "success": False,
            "error": "INVALID_TRANSITION",
            "current_status": current_status,
            "requested_status": new_status,
        }

    now = datetime.now(
        timezone.utc
    )

    update_fields = {
        "status": new_status,
        "updated_at": now,
    }

    if new_status == "Resolved":

        update_fields["resolution"] = {
            "summary": resolution_summary,

            "resolved_by": str(
                actor_user_id
            ),

            "resolved_at": now,
        }

    tickets_collection.update_one(
        {
            "ticket_id": ticket_id
        },
        {
            "$set": update_fields
        },
    )

    history_document = {
        "ticket_id": ticket_id,

        "from_status": current_status,

        "to_status": new_status,

        "changed_by": str(
            actor_user_id
        ),

        "changed_at": now,
    }

    history_result = (
        status_history_collection.insert_one(
            history_document
        )
    )

    history_document["_id"] = str(
        history_result.inserted_id
    )

    result = {
        "success": True,

        "ticket_id": ticket_id,

        "from_status": current_status,

        "to_status": new_status,

        "changed_by": str(
            actor_user_id
        ),

        "changed_at": now,
    }

    if new_status == "Resolved":
        result["resolution"] = {
            "summary": resolution_summary,

            "resolved_by": str(
                actor_user_id
            ),

            "resolved_at": now,
        }

    return result

def add_ticket_comment(
    ticket_id,
    author_user_id,
    comment,
    visibility,
    source="HUMAN",
):
    """
    Add a public or internal comment to a ticket.
    """

    ticket = tickets_collection.find_one(
        {
            "ticket_id": ticket_id
        }
    )

    if not ticket:
        return None

    comment_document = {
        "ticket_id": ticket_id,

        "author_user_id": str(
            author_user_id
        ),

        "comment": comment,

        "visibility": visibility,

        "source": source,

        "created_at": datetime.now(
            timezone.utc
        ),
    }

    result = comments_collection.insert_one(
        comment_document
    )

    comment_document["_id"] = str(
        result.inserted_id
    )

    return comment_document

def get_ticket_timeline(
    ticket_id,
    include_internal=False,
):
    """
    Return ticket status history and comments
    as one chronological timeline.
    """

    timeline = []

    status_events = status_history_collection.find(
        {
            "ticket_id": ticket_id
        }
    ).sort(
        "changed_at",
        1,
    )

    for event in status_events:

        timeline.append({
            "event_type": "STATUS_CHANGE",
            "ticket_id": ticket_id,
            "from_status": event.get(
                "from_status"
            ),
            "to_status": event.get(
                "to_status"
            ),
            "changed_by": event.get(
                "changed_by"
            ),
            "created_at": event.get(
                "changed_at"
            ),
        })

    comment_query = {
        "ticket_id": ticket_id
    }

    if not include_internal:
        comment_query["visibility"] = "PUBLIC"

    comments = comments_collection.find(
        comment_query
    ).sort(
        "created_at",
        1,
    )

    for comment in comments:

        timeline.append({
            "event_type": "COMMENT",
            "ticket_id": ticket_id,
            "author_user_id": comment.get(
                "author_user_id"
            ),
            "comment": comment.get(
                "comment"
            ),
            "visibility": comment.get(
                "visibility"
            ),
            "created_at": comment.get(
                "created_at"
            ),
        })

    timeline.sort(
        key=lambda event: event.get(
            "created_at"
        )
    )

    return timeline