from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .schemas import RetrievalCase


def load_json(
    path: str | Path,
) -> Any:
    file_path = Path(path)

    with file_path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        return json.load(handle)


def load_retrieval_cases(
    path: str | Path,
) -> list[RetrievalCase]:
    payload = load_json(path)

    if isinstance(payload, dict):
        payload = payload.get(
            "cases",
            payload,
        )

    if not isinstance(
        payload,
        list,
    ):
        raise ValueError(
            "Retrieval golden set must be a JSON array "
            "or an object with a 'cases' array."
        )

    cases = [
        RetrievalCase.from_dict(item)
        for item in payload
    ]

    case_ids = [
        case.case_id
        for case in cases
    ]

    duplicates = sorted(
        {
            case_id
            for case_id in case_ids
            if case_ids.count(case_id) > 1
        }
    )

    if duplicates:
        raise ValueError(
            "Duplicate retrieval case ids: "
            + ", ".join(duplicates)
        )

    evaluation_ticket_ids = [
        case.ticket.evaluation_ticket_id
        for case in cases
    ]

    duplicate_ticket_ids = sorted(
        {
            ticket_id
            for ticket_id in evaluation_ticket_ids
            if evaluation_ticket_ids.count(ticket_id) > 1
        }
    )

    if duplicate_ticket_ids:
        raise ValueError(
            "Duplicate evaluation ticket ids: "
            + ", ".join(duplicate_ticket_ids)
        )

    return cases