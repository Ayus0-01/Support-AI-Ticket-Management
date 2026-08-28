from datetime import datetime, timezone
import difflib

from .persistence import (
    get_ticket_response,
    update_ticket_response_status,
    update_ticket_resolution_state,
    create_resolution_feedback,
)

from AIticket.db import (
    tickets_collection,
    ticket_responses_collection,
)


from apps.tickets.services import (
    add_ticket_comment,
    transition_ticket_status,
)


def get_response_for_review(
    *,
    response_id,
):
    return get_ticket_response(
        response_id=response_id
    )


def accept_response(
    *,
    response_id,
    reviewer_id,
):
    response = get_ticket_response(
        response_id=response_id
    )

    if not response:
        raise ValueError(
            "Response not found."
        )

    if response.get("status") != "DRAFT":
        raise ValueError(
            "Only DRAFT responses can be accepted."
        )

    now = datetime.now(
        timezone.utc
    )

    update_ticket_response_status(
        response_id=response_id,
        status="SENT",
        reviewed_by_id=reviewer_id,
        reviewed_at=now,
    )

    update_ticket_resolution_state(
        ticket_id=response["ticket_id"],
        resolution_status="SENT",
        response_id=response_id,
    )

    ticket = tickets_collection.find_one(
        {
            "_id": response["ticket_id"]
        }
    )

    if ticket and ticket.get(
        "status"
    ) == "Open":
        transition_ticket_status(
            ticket_id=ticket["ticket_id"],
            new_status="In Progress",
            actor_user_id=reviewer_id,
        )

    steps_text = "\n".join(
        [
            f"{step.get('order')}. "
            f"{step.get('instruction')}"
            for step in response.get(
                "steps",
                [],
            )
        ]
    )

    comment = (
        f"{response.get('summary', '')}\n\n"
        f"{steps_text}"
    ).strip()

    add_ticket_comment(
        ticket_id=response.get(
            "ticket_number"
        ),
        author_user_id=reviewer_id,
        comment=comment,
        visibility="PUBLIC",
        source="AI",
    )

    return get_ticket_response(
        response_id=response_id
    )


def reject_response(
    *,
    response_id,
    reviewer_id,
    reason,
):
    response = get_ticket_response(
        response_id=response_id
    )

    if not response:
        raise ValueError(
            "Response not found."
        )

    if response.get("status") != "DRAFT":
        raise ValueError(
            "Only DRAFT responses can be rejected."
        )

    reason = (
        reason or ""
    ).strip()

    if not reason:
        raise ValueError(
            "Reject reason is required."
        )

    now = datetime.now(
        timezone.utc
    )

    update_ticket_response_status(
        response_id=response_id,
        status="REJECTED",
        reviewed_by_id=reviewer_id,
        reviewed_at=now,
        reject_reason=reason,
    )

    update_ticket_resolution_state(
        ticket_id=response["ticket_id"],
        resolution_status="REJECTED",
    )

    return get_ticket_response(
        response_id=response_id
    )


def edit_and_send_response(
    *,
    response_id,
    reviewer_id,
    edited_summary,
    edited_steps,
):
    response = get_ticket_response(
        response_id=response_id
    )

    if not response:
        raise ValueError(
            "Response not found."
        )

    if response.get("status") != "DRAFT":
        raise ValueError(
            "Only DRAFT responses can be edited and sent."
        )

    edited_summary = (
        edited_summary or ""
    ).strip()

    if not edited_summary:
        raise ValueError(
            "Edited summary is required."
        )

    edited_steps = (
        edited_steps or []
    )

    original_text = (
        response.get("summary", "")
        + "\n"
        + "\n".join(
            step.get(
                "instruction",
                "",
            )
            for step in response.get(
                "steps",
                [],
            )
        )
    )

    edited_text = (
        edited_summary
        + "\n"
        + "\n".join(
            step.get(
                "instruction",
                "",
            )
            for step in edited_steps
        )
    )

    edit_diff = list(
        difflib.unified_diff(
            original_text.splitlines(),
            edited_text.splitlines(),
            lineterm="",
        )
    )

    now = datetime.now(
        timezone.utc
    )

    ticket_response_update = {
        "summary": edited_summary,
        "steps": edited_steps,
    }

    ticket_responses_collection.update_one(
        {
            "_id": response["_id"]
        },
        {
            "$set": {
                **ticket_response_update,
            }
        },
    )

    update_ticket_response_status(
        response_id=response_id,
        status="EDITED_SENT",
        reviewed_by_id=reviewer_id,
        reviewed_at=now,
        edit_diff=edit_diff,
    )

    update_ticket_resolution_state(
        ticket_id=response["ticket_id"],
        resolution_status="EDITED_SENT",
        response_id=response_id,
    )

    ticket = tickets_collection.find_one(
        {
            "_id": response["ticket_id"]
        }
    )

    if ticket and ticket.get(
        "status"
    ) == "Open":
        transition_ticket_status(
            ticket_id=ticket["ticket_id"],
            new_status="In Progress",
            actor_user_id=reviewer_id,
        )

    steps_text = "\n".join(
        [
            f"{step.get('order')}. "
            f"{step.get('instruction')}"
            for step in edited_steps
        ]
    )

    comment = (
        f"{edited_summary}\n\n"
        f"{steps_text}"
    ).strip()

    add_ticket_comment(
        ticket_id=response.get(
            "ticket_number"
        ),
        author_user_id=reviewer_id,
        comment=comment,
        visibility="PUBLIC",
        source="AI",
    )

    return get_ticket_response(
        response_id=response_id
    )


def submit_feedback(
    *,
    response_id,
    user_id,
    was_helpful,
    comment="",
    resolved_ticket=False,
):
    response = get_ticket_response(
        response_id=response_id
    )

    if not response:
        raise ValueError(
            "Response not found."
        )

    return create_resolution_feedback(
        response_id=response_id,
        ticket_id=response["ticket_id"],
        user_id=user_id,
        was_helpful=was_helpful,
        comment=comment,
        resolved_ticket=resolved_ticket,
    )