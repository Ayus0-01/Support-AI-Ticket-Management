from __future__ import annotations

import json
from pathlib import Path

from apps.knowledge_base.services import (
    search_knowledge_base,
)

from AIticket.db import (
    tickets_collection,
)


OUTPUT = Path(
    "evaluation_data/retrieval_candidates.json"
)

DEFAULT_LIMIT = 100


def _string(
    value,
) -> str:
    if value is None:
        return ""

    if isinstance(
        value,
        dict,
    ):
        for key in (
            "name",
            "value",
            "code",
            "department",
            "id",
        ):
            if value.get(key) is not None:
                return str(
                    value[key]
                ).strip()

        return ""

    return str(
        value
    ).strip()


def _extract_classification(
    ticket: dict,
):
    classification = (
        ticket.get(
            "classification"
        )
        or {}
    )

    category = (
        classification.get(
            "category"
        )
        or {}
    )

    sub_category = (
        classification.get(
            "sub_category"
        )
        or {}
    )

    if isinstance(
        category,
        dict,
    ):
        category_value = (
            category.get(
                "value"
            )
        )
    else:
        category_value = category

    if isinstance(
        sub_category,
        dict,
    ):
        sub_category_value = (
            sub_category.get(
                "value"
            )
        )
    else:
        sub_category_value = sub_category

    return (
        _string(
            category_value
        ),
        _string(
            sub_category_value
        ),
    )


def _ticket_text(
    ticket: dict,
):
    subject = _string(
        ticket.get(
            "subject"
        )
    )

    description = _string(
        ticket.get(
            "description"
        )
    )

    return (
        subject,
        description,
    )


def build_candidates(
    limit: int = DEFAULT_LIMIT,
):
    tickets = list(
        tickets_collection.find(
            {},
            {
                "_id": 1,
                "subject": 1,
                "description": 1,
                "classification": 1,
                "department": 1,
            },
        )
        .sort(
            "created_at",
            -1,
        )
        .limit(limit)
    )

    output = []

    for ticket in tickets:
        subject, description = (
            _ticket_text(ticket)
        )

        category, _sub_category = (
            _extract_classification(
                ticket
            )
        )

        department = _string(
            ticket.get(
                "department"
            )
        )

        if not subject and not description:
            continue

        query = (
            f"{subject}\n"
            f"{description}"
        ).strip()

        try:
            results = (
                search_knowledge_base(
                    query=query,
                    status="PUBLISHED",
                    limit=10,
                    top_k=5,
                    category=(
                        category
                        or None
                    ),
                    department=(
                        department
                        or None
                    ),
                    include_internal=False,
                )
            )

        except Exception as exc:
            output.append(
                {
                    "id": (
                        f"CAND-"
                        f"{len(output) + 1:03d}"
                    ),
                    "ticket_id": str(
                        ticket.get(
                            "_id"
                        )
                    ),
                    "subject": subject,
                    "description": description,
                    "category": (
                        category
                        or None
                    ),
                    "department": (
                        department
                        or None
                    ),
                    "candidate_articles": [],
                    "expected_article_ids": [],
                    "review_status": (
                        "SEARCH_ERROR"
                    ),
                    "search_error": str(
                        exc
                    ),
                }
            )
            continue

        candidates = []

        for rank, result in enumerate(
            results,
            start=1,
        ):
            article_id = result.get(
                "article_id"
            )

            if not article_id:
                continue

            candidates.append(
                {
                    "rank": rank,
                    "article_id": str(
                        article_id
                    ),
                    "article_title": result.get(
                        "article_title"
                    ),
                    "heading_path": result.get(
                        "heading_path",
                        "",
                    ),
                    "score": result.get(
                        "rrf_score",
                        result.get(
                            "score"
                        ),
                    ),
                }
            )

        output.append(
            {
                "id": (
                    f"CAND-"
                    f"{len(output) + 1:03d}"
                ),
                "ticket_id": str(
                    ticket.get(
                        "_id"
                    )
                ),
                "subject": subject,
                "description": description,
                "category": (
                    category
                    or None
                ),
                "department": (
                    department
                    or None
                ),
                "candidate_articles": candidates,
                "expected_article_ids": [],
                "review_status": (
                    "UNREVIEWED"
                ),
            }
        )

    return output


def main():
    candidates = build_candidates()

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            candidates,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"CANDIDATES WRITTEN: "
        f"{len(candidates)}"
    )

    print(
        f"OUTPUT: {OUTPUT}"
    )

    print(
        "NEXT: Manually populate "
        "expected_article_ids and change "
        "review_status to REVIEWED."
    )


if __name__ == "__main__":
    main()