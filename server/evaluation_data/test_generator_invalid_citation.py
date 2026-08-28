import json
import os
import sys
from pathlib import Path
from unittest.mock import patch


BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "AIticket.settings",
)

import django

django.setup()


from apps.knowledge_base.generator import (
    generate_resolution,
)


PACKED_CONTEXT = """
[SOURCE:article-valid#0]
Title: Test Article
Section: Test Article > Troubleshooting
Updated: 2026-08-28
---
Perform the documented troubleshooting check.
""".strip()


MOCK_RESPONSE = json.dumps(
    {
        "sufficient_context": True,
        "summary": "Test resolution",
        "steps": [
            {
                "order": 1,
                "instruction": "Perform an unsupported action.",
                "sources": [
                    "article-fake#0"
                ],
                "requires_approval": False,
            }
        ],
        "sources": [
            "article-fake#0"
        ],
        "escalation_recommended": False,
        "escalation_reason": None,
    }
)


print("=" * 80)
print("M2 GENERATOR INVALID-CITATION TEST")
print("=" * 80)


with patch(
    "apps.knowledge_base.generator._call_ollama",
    return_value=MOCK_RESPONSE,
):
    resolution = generate_resolution(
        subject="Test issue",
        description="A test issue with sufficient KB context.",
        category="HARDWARE",
        subcategory="Test",
        already_tried="Restarted once.",
        severity="MEDIUM",
        packed_context=PACKED_CONTEXT,
        retrieval_results=[
            {
                "article_id": "article-valid",
                "chunk_index": 0,
                "article_title": "Test Article",
                "rerank_score": 5.0,
            }
        ],
        classification_confidence=1.0,
    )


print("\nRESULT:")
print(
    json.dumps(
        resolution,
        indent=2,
    )
)


print("\n" + "-" * 80)
print("ASSERTIONS")
print("-" * 80)


assert resolution["steps_generated"] == 1

assert resolution["steps_dropped"] == 1

assert resolution["steps"] == []

assert resolution["sufficient_context"] is False

assert resolution["escalation_recommended"] is True

assert len(
    resolution["dropped_details"]
) == 1

assert (
    resolution["dropped_details"][0]["reason"]
    == "NO_VALID_CITATION"
)

print("Generated step detected: PASS")
print("Invalid citation dropped: PASS")
print("Steps reduced to []: PASS")
print("sufficient_context = FALSE: PASS")
print("Escalation enabled: PASS")
print("Dropped reason recorded: PASS")


print("\n" + "=" * 80)
print("GENERATOR INVALID-CITATION TEST: PASS")
print("=" * 80)