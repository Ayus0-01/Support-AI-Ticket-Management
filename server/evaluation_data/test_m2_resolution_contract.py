import os
import sys
from pathlib import Path
from unittest.mock import patch

from bson import ObjectId


BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "AIticket.settings",
)

import django

django.setup()


from apps.knowledge_base.resolution_service import (
    generate_and_persist_resolution,
)

from AIticket.db import (
    tickets_collection,
    ticket_responses_collection,
    response_citations_collection,
)


print("=" * 80)
print("M2 RESOLUTION CONTRACT TEST")
print("=" * 80)


ticket_id = ObjectId()
article_id = ObjectId()


ticket = {
    "_id": ticket_id,
    "ticket_id": "TEST-M2-CONTRACT-001",
    "subject": "VPN connection timeout",
    "description": "Corporate VPN keeps timing out.",
    "category": "VPN",
    "subcategory": "Timeout",
    "severity": "HIGH",
    "affected_system": "Corporate VPN",
    "department": "Finance",
}

tickets_collection.insert_one(
    ticket
)


retrieval = {
    "queries": [
        "corporate VPN connection timeout resolution",
    ],
    "results": [
        {
            "article_id": article_id,
            "article_title": "VPN Guide",
            "chunk_index": 0,
            "heading_path": "VPN Guide > Timeout",
            "content": "Verify VPN connectivity and retry.",
            "rerank_score": 4.5,
        }
    ],
    "context": (
        f"[SOURCE:{article_id}#0]\n"
        "Title: VPN Guide\n"
        "Section: VPN Guide > Timeout\n"
        "---\n"
        "Verify VPN connectivity and retry."
    ),
}


resolution = {
    "sufficient_context": True,
    "summary": "Verify VPN connectivity.",
    "steps": [
        {
            "order": 1,
            "instruction": "Verify VPN connectivity.",
            "sources": [
                f"[SOURCE:{article_id}#0]"
            ],
            "requires_approval": False,
        }
    ],
    "sources": [
        f"[SOURCE:{article_id}#0]"
    ],
    "escalation_recommended": False,
    "escalation_reason": None,
    "steps_generated": 1,
    "steps_dropped": 0,
    "dropped_details": [],
    "confidence": 0.91,
    "confidence_parts": {
        "top_rerank": 4.5,
        "citation_coverage": 1.0,
        "classification": 0.95,
    },
    "confidence_label": "PROVISIONAL",
}


print("\n1. EXECUTE RESOLUTION SERVICE")

with patch(
    "apps.knowledge_base.resolution_service.retrieve_for_ticket",
    return_value=retrieval,
), patch(
    "apps.knowledge_base.resolution_service.generate_resolution",
    return_value=resolution,
):
    response = generate_and_persist_resolution(
        ticket=ticket,
        classification_confidence=0.95,
    )

assert response is not None
print("RESOLUTION SERVICE: PASS")


print("\n2. RESPONSE CONTRACT")

stored_response = ticket_responses_collection.find_one(
    {
        "_id": response["_id"]
    }
)

assert stored_response is not None
assert stored_response["ticket_id"] == ticket_id
assert stored_response["status"] == "DRAFT"
assert stored_response["sufficient_context"] is True
assert stored_response["retrieval_log_id"] is not None
assert stored_response["queries_used"]
assert stored_response["chunks_retrieved"] == 1
assert stored_response["steps"]
assert stored_response["sources"]

print("TICKET RESPONSE: PASS")


print("\n3. CITATION CONTRACT")

citations = list(
    response_citations_collection.find(
        {
            "response_id": response["_id"]
        }
    )
)

assert len(citations) == 1

citation = citations[0]

assert citation["ticket_id"] == ticket_id
assert citation["step_order"] == 1
assert citation["article_id"] == article_id
assert citation["article_title"] == "VPN Guide"
assert citation["chunk_index"] == 0
assert citation["heading_path"] == (
    "VPN Guide > Timeout"
)
assert citation["snippet"]
assert citation["rerank_score"] == 4.5
assert citation["retrieval_rank"] == 1

print("RESPONSE CITATION: PASS")


print("\n4. TICKET RESOLUTION STATE")

stored_ticket = tickets_collection.find_one(
    {
        "_id": ticket_id
    }
)

assert stored_ticket is not None
assert stored_ticket.get("has_resolution") is True
assert stored_ticket.get("resolution_status") == "DRAFT"
assert stored_ticket.get("latest_response_id") == response["_id"]

print("TICKET RESOLUTION STATE: PASS")


print("\n" + "=" * 80)
print("M2 RESOLUTION CONTRACT TEST: PASS")
print("=" * 80)