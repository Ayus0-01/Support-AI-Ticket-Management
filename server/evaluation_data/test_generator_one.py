import json
import os
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "AIticket.settings",
)

import django

django.setup()


from apps.knowledge_base.evaluation.loader import (
    load_retrieval_cases,
)

from apps.knowledge_base.ticket_retrieval import (
    retrieve_for_ticket,
)

from apps.knowledge_base.packing import (
    pack_context,
)

from apps.knowledge_base.generator import (
    generate_resolution,
)


CASE_ID = "R037"


cases = load_retrieval_cases(
    BASE_DIR
    / "evaluation_data"
    / "retrieval_golden.json"
)

case = next(
    case
    for case in cases
    if case.case_id == CASE_ID
)

ticket = case.ticket.to_ticket_dict()

print("=" * 80)
print("M2 GENERATOR END-TO-END TEST")
print("=" * 80)

print("\nCASE:", case.case_id)
print("TICKET:", ticket["ticket_id"])
print("SUBJECT:", ticket["subject"])
print("EXPECTED ARTICLES:", case.expected_article_ids)


print("\n" + "-" * 80)
print("STEP 1 - RETRIEVAL")
print("-" * 80)

retrieval = retrieve_for_ticket(
    ticket=ticket,
    include_internal=False,
    limit=30,
    top_k=5,
    rerank_candidates=20,
    context_budget=4000,
)

print("QUERIES:")
for query in retrieval["queries"]:
    print(" -", query)

print("\nRETRIEVED RESULTS:")
for rank, result in enumerate(
    retrieval["results"],
    start=1,
):
    print(
        {
            "rank": rank,
            "article_id": str(
                result.get("article_id")
            ),
            "title": result.get(
                "article_title"
            ),
            "sub_category": result.get(
                "sub_category"
            ),
            "rerank_score": result.get(
                "rerank_score"
            ),
        }
    )


print("\n" + "-" * 80)
print("STEP 2 - CONTEXT PACKING")
print("-" * 80)

packed_context = pack_context(
    retrieval["results"],
    budget_tokens=4000,
)

print("PACKED CONTEXT:\n")
print(packed_context)


print("\n" + "-" * 80)
print("STEP 3 - GENERATION")
print("-" * 80)

resolution = generate_resolution(
    subject=ticket["subject"],
    description=ticket["description"],
    category=ticket["category"],
    subcategory=ticket["subcategory"],
    already_tried=ticket["already_tried"],
    severity=ticket["severity"],
    packed_context=packed_context,
    retrieval_results=retrieval["results"],
    classification_confidence=1.0,
)

print(
    json.dumps(
        resolution,
        indent=2,
        default=str,
    )
)


print("\n" + "-" * 80)
print("STEP 4 - BASIC ASSERTIONS")
print("-" * 80)

assert isinstance(
    resolution,
    dict,
)

assert "sufficient_context" in resolution
assert "summary" in resolution
assert "steps" in resolution
assert "sources" in resolution
assert "escalation_recommended" in resolution

if resolution["sufficient_context"]:
    assert resolution["steps"], (
        "Expected grounded steps when "
        "sufficient_context is true."
    )

    for step in resolution["steps"]:
        assert step.get("sources"), (
            "Every retained step must "
            "have at least one source."
        )

        for source in step["sources"]:
            assert source.startswith(
                "[SOURCE:"
            )
            assert source in packed_context

print("BASIC ASSERTIONS: PASS")

print("\n" + "=" * 80)
print("GENERATOR END-TO-END TEST COMPLETE")
print("=" * 80)