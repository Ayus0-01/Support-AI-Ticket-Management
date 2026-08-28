import os
import sys
from pathlib import Path

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


from apps.knowledge_base.persistence import (
    create_retrieval_log,
    create_ticket_response,
    create_response_citations,
    create_resolution_feedback,
    record_kb_gap,
)

from AIticket.db import (
    retrieval_logs_collection,
    ticket_responses_collection,
    response_citations_collection,
    resolution_feedback_collection,
    kb_gaps_collection,
)


print("=" * 80)
print("M2 PERSISTENCE CONTRACT TEST")
print("=" * 80)


ticket_id = ObjectId()
user_id = ObjectId()
article_id = ObjectId()


retrieval_results = [
    {
        "article_id": article_id,
        "article_title": "VPN Guide",
        "chunk_index": 0,
        "heading_path": "VPN Guide > Timeout",
        "content": "Verify VPN connectivity and retry the connection.",
        "rerank_score": 4.2,
    }
]


print("\n1. CREATE RETRIEVAL LOG")

retrieval_log = create_retrieval_log(
    ticket_id=ticket_id,
    queries_used=[
        "corporate VPN connection timeout resolution"
    ],
    chunks_retrieved=1,
    results=retrieval_results,
)

assert retrieval_log["_id"] is not None
assert retrieval_log["ticket_id"] == ticket_id
assert retrieval_log["queries_used"]
assert retrieval_log["chunks_retrieved"] == 1
assert len(retrieval_log["results"]) == 1

logged_result = retrieval_log["results"][0]

assert logged_result["article_id"] == article_id
assert logged_result["article_title"] == "VPN Guide"
assert logged_result["chunk_index"] == 0
assert logged_result["rerank_score"] == 4.2
assert logged_result["retrieval_rank"] == 1

print("RETRIEVAL LOG: PASS")


print("\n2. CREATE TICKET RESPONSE")

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
        "top_rerank": 4.2,
        "citation_coverage": 1.0,
        "classification": 0.95,
    },
}

ticket = {
    "_id": ticket_id,
    "ticket_id": "TEST-M2-CONTRACT-001",
}

response = create_ticket_response(
    ticket=ticket,
    resolution=resolution,
    retrieval_log=retrieval_log,
    queries_used=[
        "corporate VPN connection timeout resolution"
    ],
)

assert response["_id"] is not None
assert response["ticket_id"] == ticket_id
assert response["retrieval_log_id"] == retrieval_log["_id"]
assert response["status"] == "DRAFT"
assert response["sufficient_context"] is True
assert response["steps"]
assert response["sources"]
assert response["queries_used"]
assert response["chunks_retrieved"] == 1
assert response["confidence"] == 0.91

print("TICKET RESPONSE: PASS")


print("\n3. CREATE RESPONSE CITATIONS")

citations = create_response_citations(
    response=response,
    retrieval_results=retrieval_results,
)

assert len(citations) == 1

citation = citations[0]

assert citation["response_id"] == response["_id"]
assert citation["ticket_id"] == ticket_id
assert citation["step_order"] == 1
assert citation["article_id"] == article_id
assert citation["article_title"] == "VPN Guide"
assert citation["chunk_index"] == 0
assert citation["heading_path"] == "VPN Guide > Timeout"
assert citation["snippet"]
assert citation["rerank_score"] == 4.2
assert citation["retrieval_rank"] == 1

print("RESPONSE CITATION: PASS")


print("\n4. CREATE RESOLUTION FEEDBACK")

feedback = create_resolution_feedback(
    response_id=response["_id"],
    ticket_id=ticket_id,
    user_id=user_id,
    was_helpful=True,
    comment="The resolution was useful.",
    resolved_ticket=True,
)

assert feedback["_id"] is not None
assert feedback["response_id"] == response["_id"]
assert feedback["ticket_id"] == ticket_id
assert feedback["user_id"] == user_id
assert feedback["was_helpful"] is True
assert feedback["comment"] == "The resolution was useful."
assert feedback["resolved_ticket"] is True

print("RESOLUTION FEEDBACK: PASS")


print("\n5. RECORD KB GAP")

gap_result = record_kb_gap(
    ticket_id=ticket_id,
    reason="No documented procedure found.",
)

assert gap_result is not None

gap = kb_gaps_collection.find_one(
    {
        "ticket_id": ticket_id,
        "status": "OPEN",
    }
)

assert gap is not None
assert gap["ticket_id"] == ticket_id
assert gap["status"] == "OPEN"
assert gap["occurrence_count"] == 1
assert gap["last_reason"] == (
    "No documented procedure found."
)
assert gap["first_seen_at"] is not None
assert gap["updated_at"] is not None

print("KB GAP: PASS")


print("\n6. DATABASE RELATIONSHIPS")

stored_response = ticket_responses_collection.find_one(
    {"_id": response["_id"]}
)

stored_log = retrieval_logs_collection.find_one(
    {"_id": retrieval_log["_id"]}
)

stored_citation = response_citations_collection.find_one(
    {"_id": citation["_id"]}
)

stored_feedback = resolution_feedback_collection.find_one(
    {"_id": feedback["_id"]}
)

assert stored_response is not None
assert stored_log is not None
assert stored_citation is not None
assert stored_feedback is not None

assert stored_response["retrieval_log_id"] == stored_log["_id"]
assert stored_citation["response_id"] == stored_response["_id"]
assert stored_feedback["response_id"] == stored_response["_id"]
assert stored_feedback["ticket_id"] == stored_response["ticket_id"]

print("DATABASE RELATIONSHIPS: PASS")


print("\n" + "=" * 80)
print("M2 PERSISTENCE CONTRACT TEST: PASS")
print("=" * 80)