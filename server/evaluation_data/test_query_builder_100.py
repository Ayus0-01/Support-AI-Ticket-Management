from __future__ import annotations

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import os

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "AIticket.settings",
)

import django

django.setup()

from apps.knowledge_base.evaluation.loader import (
    load_retrieval_cases,
)

from apps.knowledge_base.query_builder import (
    build_search_queries,
)


cases = load_retrieval_cases(
    "evaluation_data/retrieval_golden.json"
)

passed = 0
failed = []

print("=" * 70)
print("QUERY BUILDER REGRESSION")
print("=" * 70)

for case in cases:
    try:
        queries = build_search_queries(
            subject=case.ticket.subject,
            description=case.ticket.description,
            category=case.ticket.category,
            affected_system=case.ticket.affected_system,
        )

        print(
            "PASS",
            case.case_id,
            case.ticket.evaluation_ticket_id,
            "->",
            queries,
        )

        passed += 1

    except Exception as exc:
        print(
            "FAIL",
            case.case_id,
            case.ticket.evaluation_ticket_id,
            "->",
            repr(exc),
        )

        failed.append(
            (
                case.case_id,
                case.ticket.evaluation_ticket_id,
                str(exc),
            )
        )


print("=" * 70)
print("PASSED:", passed)
print("FAILED:", len(failed))

if failed:
    print("FAILED CASES:")

    for case_id, ticket_id, error in failed:
        print(
            {
                "case_id": case_id,
                "ticket_id": ticket_id,
                "error": error,
            }
        )

print("=" * 70)