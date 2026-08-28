import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from apps.knowledge_base.guardrails.citations import (
    enforce_citations,
    extract_valid_source_ids,
)


PACKED_CONTEXT = """
[ SOURCE_PLACEHOLDER ]
"""

# Replace the placeholder spacing with an actual marker below.
PACKED_CONTEXT = """
Knowledge Base excerpt.

[SOURCE:article-123#0]

This is supported troubleshooting content.

[SOURCE:article-456#2]

This is another supported excerpt.
""".strip()


def run_test(
    name,
    resolution,
):
    result = enforce_citations(
        resolution,
        PACKED_CONTEXT,
    )

    print("\n" + "=" * 80)
    print(name)
    print("=" * 80)
    print("INPUT STEPS:", len(resolution.get("steps", [])))
    print("KEPT STEPS:", len(result.get("steps", [])))
    print("DROPPED:", result.get("steps_dropped"))
    print("SUFFICIENT CONTEXT:", result.get("sufficient_context"))
    print("ESCALATION:", result.get("escalation_recommended"))
    print("DROPPED DETAILS:", result.get("dropped_details"))
    print("STEPS:", result.get("steps"))

    return result


print("=" * 80)
print("CITATION GUARDRAIL TEST")
print("=" * 80)

print("\nVALID SOURCES FOUND:")
print(
    extract_valid_source_ids(
        PACKED_CONTEXT
    )
)


run_test(
    "TEST 1 - VALID CITATION",
    {
        "sufficient_context": True,
        "summary": "Supported resolution",
        "steps": [
            {
                "order": 1,
                "instruction": "Perform the documented check.",
                "sources": [
                    "article-123#0"
                ],
            }
        ],
        "sources": [
            "article-123#0"
        ],
        "escalation_recommended": False,
        "escalation_reason": None,
    },
)


run_test(
    "TEST 2 - BRACKETED VALID CITATION",
    {
        "sufficient_context": True,
        "summary": "Supported resolution",
        "steps": [
            {
                "order": 1,
                "instruction": "Perform the documented check.",
                "sources": [
                    "[SOURCE:article-123#0]"
                ],
            }
        ],
        "sources": [],
        "escalation_recommended": False,
        "escalation_reason": None,
    },
)


run_test(
    "TEST 3 - INVALID CITATION",
    {
        "sufficient_context": True,
        "summary": "Unsupported resolution",
        "steps": [
            {
                "order": 1,
                "instruction": "Perform an unsupported action.",
                "sources": [
                    "article-999#0"
                ],
            }
        ],
        "sources": [],
        "escalation_recommended": False,
        "escalation_reason": None,
    },
)


run_test(
    "TEST 4 - NO CITATION",
    {
        "sufficient_context": True,
        "summary": "Uncited resolution",
        "steps": [
            {
                "order": 1,
                "instruction": "Perform an uncited action.",
                "sources": [],
            }
        ],
        "sources": [],
        "escalation_recommended": False,
        "escalation_reason": None,
    },
)


run_test(
    "TEST 5 - MIXED VALID AND INVALID",
    {
        "sufficient_context": True,
        "summary": "Mixed sources",
        "steps": [
            {
                "order": 1,
                "instruction": "Use supported documentation.",
                "sources": [
                    "article-123#0",
                    "article-999#0",
                    "[SOURCE:article-456#2]",
                ],
            }
        ],
        "sources": [],
        "escalation_recommended": False,
        "escalation_reason": None,
    },
)


run_test(
    "TEST 6 - ALL STEPS INVALID",
    {
        "sufficient_context": True,
        "summary": "No support",
        "steps": [
            {
                "order": 1,
                "instruction": "Unsupported action one.",
                "sources": [
                    "article-999#0"
                ],
            },
            {
                "order": 2,
                "instruction": "Unsupported action two.",
                "sources": [],
            },
        ],
        "sources": [],
        "escalation_recommended": False,
        "escalation_reason": None,
    },
)

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)