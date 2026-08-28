from unittest.mock import patch

from apps.knowledge_base.generator import (
    generate_resolution,
)


PACKED_CONTEXT = """
[SOURCE:abc123#0]
Title: VPN Troubleshooting Guide
Section: Connectivity
Updated: 2026-08-24T12:00:00+00:00
---
Verify network connectivity before changing VPN settings.
""".strip()


VALID_MODEL_RESPONSE = """
{
  "sufficient_context": true,
  "summary": "The VPN issue should first be checked at the network and configuration level.",
  "steps": [
    {
      "order": 1,
      "instruction": "Verify network connectivity.",
      "sources": ["abc123#0"],
      "requires_approval": false
    },
    {
      "order": 2,
      "instruction": "Verify VPN configuration.",
      "sources": ["abc123#0"],
      "requires_approval": false
    }
  ],
  "sources": ["abc123#0"],
  "escalation_recommended": false,
  "escalation_reason": null
}
""".strip()


def test_valid_generation():
    with patch(
        "apps.knowledge_base.generator._call_ollama",
        return_value=VALID_MODEL_RESPONSE,
    ):
        result = generate_resolution(
            subject="VPN connection timeout",
            description="VPN cannot connect.",
            category="VPN",
            subcategory="Timeout",
            severity="HIGH",
            packed_context=PACKED_CONTEXT,
            retrieval_results=[
                {
                    "rerank_score": 0.90,
                }
            ],
            classification_confidence=0.92,
        )

    assert result["sufficient_context"] is True
    assert len(result["steps"]) == 2
    assert result["steps_dropped"] == 0
    assert result["confidence"] > 0
    assert (
        result["confidence_label"]
        == "PROVISIONAL"
    )


def test_invalid_citation_is_dropped():
    response = """
    {
      "sufficient_context": true,
      "summary": "VPN troubleshooting.",
      "steps": [
        {
          "order": 1,
          "instruction": "Verify connectivity.",
          "sources": ["abc123#0"],
          "requires_approval": false
        },
        {
          "order": 2,
          "instruction": "Call a network administrator.",
          "sources": ["fake999#4"],
          "requires_approval": false
        }
      ],
      "sources": ["abc123#0"],
      "escalation_recommended": false,
      "escalation_reason": null
    }
    """.strip()

    with patch(
        "apps.knowledge_base.generator._call_ollama",
        return_value=response,
    ):
        result = generate_resolution(
            subject="VPN timeout",
            description="Cannot connect.",
            category="VPN",
            packed_context=PACKED_CONTEXT,
            retrieval_results=[
                {
                    "rerank_score": 0.90,
                }
            ],
            classification_confidence=0.92,
        )

    assert len(result["steps"]) == 1
    assert result["steps_dropped"] == 1
    assert (
        result["dropped_details"][0]["reason"]
        == "NO_VALID_CITATION"
    )


def test_destructive_action_requires_approval():
    response = """
    {
      "sufficient_context": true,
      "summary": "Credential maintenance.",
      "steps": [
        {
          "order": 1,
          "instruction": "Reset your password.",
          "sources": ["abc123#0"],
          "requires_approval": false
        }
      ],
      "sources": ["abc123#0"],
      "escalation_recommended": false,
      "escalation_reason": null
    }
    """.strip()

    with patch(
        "apps.knowledge_base.generator._call_ollama",
        return_value=response,
    ):
        result = generate_resolution(
            subject="Password issue",
            description="Password problem.",
            category="SECURITY",
            packed_context=PACKED_CONTEXT,
            retrieval_results=[
                {
                    "rerank_score": 0.90,
                }
            ],
            classification_confidence=0.92,
        )

    step = result["steps"][0]

    assert step["requires_approval"] is True
    assert step["is_destructive"] is True


def test_invalid_json_repair():
    repaired_response = VALID_MODEL_RESPONSE

    with patch(
        "apps.knowledge_base.generator._call_ollama",
        side_effect=[
            "NOT VALID JSON",
            repaired_response,
        ],
    ):
        result = generate_resolution(
            subject="VPN timeout",
            description="Cannot connect.",
            category="VPN",
            packed_context=PACKED_CONTEXT,
            retrieval_results=[
                {
                    "rerank_score": 0.90,
                }
            ],
            classification_confidence=0.92,
        )

    assert result["sufficient_context"] is True
    assert len(result["steps"]) == 2


def test_empty_context_refuses():
    result = generate_resolution(
        subject="Unknown issue",
        description="Something is broken.",
        category="UNKNOWN",
        packed_context="",
    )

    assert result["sufficient_context"] is False
    assert result["steps"] == []
    assert result["escalation_recommended"] is True


if __name__ == "__main__":
    test_valid_generation()
    test_invalid_citation_is_dropped()
    test_destructive_action_requires_approval()
    test_invalid_json_repair()
    test_empty_context_refuses()

    print("ALL GENERATOR TESTS: PASS")