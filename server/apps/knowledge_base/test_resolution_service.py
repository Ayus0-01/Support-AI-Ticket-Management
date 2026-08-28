from unittest.mock import patch

from bson import ObjectId

from apps.knowledge_base.resolution_service import (
    generate_and_persist_resolution,
)


def main():
    ticket = {
        "_id": ObjectId(),
        "ticket_id": "TEST-M2-SERVICE-001",
        "subject": "VPN connection timeout",
        "description": (
            "Company VPN keeps timing out."
        ),
        "category": "VPN",
        "subcategory": "Timeout",
        "severity": "HIGH",
        "affected_system": "Corporate VPN",
        "department": "Finance",
    }

    retrieval = {
        "queries": [
            "Corporate VPN connection timeout resolution",
        ],
        "results": [
            {
                "article_id": ObjectId(),
                "article_title": "VPN Guide",
                "chunk_index": 0,
                "rerank_score": 0.91,
            }
        ],
        "context": (
            "[SOURCE:"
            + "000000000000000000000000"
            + "#0]\n"
            "Title: VPN Guide\n"
            "---\n"
            "Verify VPN connectivity."
        ),
    }

    # Make the source in the mocked resolution match
    # the source marker in the mocked retrieval context.
    article_id = str(
        retrieval["results"][0][
            "article_id"
        ]
    )

    retrieval["context"] = (
        f"[SOURCE:{article_id}#0]\n"
        "Title: VPN Guide\n"
        "---\n"
        "Verify VPN connectivity."
    )

    resolution = {
        "sufficient_context": True,
        "summary": "Verify VPN connectivity.",
        "steps": [
            {
                "order": 1,
                "instruction": (
                    "Verify VPN connectivity."
                ),
                "sources": [
                    f"{article_id}#0"
                ],
                "requires_approval": False,
            }
        ],
        "sources": [
            f"{article_id}#0"
        ],
        "escalation_recommended": False,
        "escalation_reason": None,
        "steps_generated": 1,
        "steps_dropped": 0,
        "dropped_details": [],
        "confidence": 0.88,
        "confidence_parts": {},
        "confidence_label": "PROVISIONAL",
    }

    with patch(
        "apps.knowledge_base.resolution_service.retrieve_for_ticket",
        return_value=retrieval,
    ), patch(
        "apps.knowledge_base.resolution_service.generate_resolution",
        return_value=resolution,
    ):
        response = (
            generate_and_persist_resolution(
                ticket=ticket,
                classification_confidence=0.92,
            )
        )

    assert response["status"] == "DRAFT"
    assert response[
        "sufficient_context"
    ] is True

    print(
        "PERSISTED RESPONSE:",
        response["_id"],
    )

    print(
        "ALL RESOLUTION SERVICE TESTS: PASS"
    )


if __name__ == "__main__":
    main()