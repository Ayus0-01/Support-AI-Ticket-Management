from datetime import datetime, timezone
from bson import ObjectId

from apps.knowledge_base.persistence import (
    create_retrieval_log,
    create_ticket_response,
    create_response_citations,
)


def main():
    ticket = {
        "_id": ObjectId(),
        "ticket_id": "TEST-M2-PERSIST-001",
    }

    results = [
        {
            "article_id": ObjectId(),
            "article_title": "VPN Guide",
            "chunk_index": 0,
            "rerank_score": 0.91,
        }
    ]

    retrieval_log = create_retrieval_log(
        ticket_id=ticket["_id"],
        queries_used=[
            "Corporate VPN connection timeout resolution"
        ],
        chunks_retrieved=1,
        results=results,
    )

    print(
        "RETRIEVAL LOG:",
        retrieval_log["_id"],
    )

    response = create_ticket_response(
        ticket=ticket,
        resolution={
            "sufficient_context": True,
            "summary": "Verify VPN connectivity.",
            "steps": [
                {
                    "order": 1,
                    "instruction": (
                        "Verify network connectivity."
                    ),
                    "sources": [
                        f"[SOURCE:{results[0]['article_id']}#0]"
                    ],
                    "requires_approval": False,
                }
            ],
            "sources": [
                f"[SOURCE:{results[0]['article_id']}#0]"
            ],
            "escalation_recommended": False,
            "escalation_reason": None,
            "steps_generated": 1,
            "steps_dropped": 0,
            "dropped_details": [],
            "confidence": 0.88,
            "confidence_parts": {
                "top_rerank": 0.91,
                "citation_coverage": 1.0,
                "classification": 0.92,
            },
        },
        retrieval_log=retrieval_log,
        queries_used=[
            "Corporate VPN connection timeout resolution"
        ],
    )

    print(
        "TICKET RESPONSE:",
        response["_id"],
    )

    citations = create_response_citations(
        response=response,
        retrieval_results=results,
    )

    print(
        "CITATIONS:",
        len(citations),
    )

    assert response["status"] == "DRAFT"
    assert response["sufficient_context"] is True
    assert response["steps_dropped"] == 0
    assert len(citations) == 1

    print("ALL PERSISTENCE TESTS: PASS")


if __name__ == "__main__":
    main()