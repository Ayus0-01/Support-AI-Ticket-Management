import json
import urllib.request

from .confidence import calculate_provisional_confidence
from .guardrails.citations import enforce_citations
from .guardrails.destructive import (
    enforce_destructive_guardrail,
)


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen3:4b"

REQUIRED_FIELDS = {
    "sufficient_context",
    "summary",
    "steps",
    "sources",
    "escalation_recommended",
    "escalation_reason",
}


def _call_ollama(prompt, timeout=300):
    payload = json.dumps(
        {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "think": False,
            "format": "json",
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(
        request,
        timeout=timeout,
    ) as response:
        data = json.loads(
            response.read().decode("utf-8")
        )

    return data.get(
        "response",
        "",
    )


def _extract_json(text):
    text = (
        text or ""
    ).strip()

    if text.startswith("```"):
        lines = text.splitlines()

        if lines:
            lines = lines[1:]

        if (
            lines
            and lines[-1].strip()
            == "```"
        ):
            lines = lines[:-1]

        text = "\n".join(
            lines
        ).strip()

    return json.loads(text)


def _validate_resolution(data):
    if not isinstance(
        data,
        dict,
    ):
        raise ValueError(
            "Resolution must be a JSON object."
        )

    missing = (
        REQUIRED_FIELDS
        - set(data.keys())
    )

    if missing:
        raise ValueError(
            "Missing fields: "
            + ", ".join(
                sorted(missing)
            )
        )

    if not isinstance(
        data["sufficient_context"],
        bool,
    ):
        raise ValueError(
            "sufficient_context must be boolean."
        )

    if not isinstance(
        data["summary"],
        str,
    ):
        raise ValueError(
            "summary must be a string."
        )

    if not isinstance(
        data["steps"],
        list,
    ):
        raise ValueError(
            "steps must be a list."
        )

    if not isinstance(
        data["sources"],
        list,
    ):
        raise ValueError(
            "sources must be a list."
        )

    if not isinstance(
        data["escalation_recommended"],
        bool,
    ):
        raise ValueError(
            "escalation_recommended "
            "must be boolean."
        )

    if not (
        data["escalation_reason"]
        is None
        or isinstance(
            data["escalation_reason"],
            str,
        )
    ):
        raise ValueError(
            "escalation_reason must be "
            "string or null."
        )

    return data


def _build_prompt(
    *,
    subject,
    description,
    category,
    subcategory,
    already_tried,
    packed_context,
):
    return f"""
You are an IT support resolution assistant.

Produce troubleshooting steps using ONLY
the provided knowledge base excerpts.

Rules:
- Every step MUST cite a source using the
  form article_id#chunk_index.
- The source must correspond to a [SOURCE:article_id#chunk_index]
  marker that actually appears in the supplied context.
- If the excerpts do not cover the problem,
  set sufficient_context to false and return
  an empty steps array.
- Do NOT improvise from general knowledge.
- Return ONLY valid JSON.
- Do not include markdown or commentary.

TICKET
Subject: {subject}
Description: {description}
Category: {category}
Subcategory: {subcategory}
Already tried: {already_tried}

KNOWLEDGE BASE EXCERPTS
{packed_context}

OUTPUT JSON
{{
  "sufficient_context": true,
  "summary": "Brief resolution summary",
  "steps": [
    {{
      "order": 1,
      "instruction": "Supported troubleshooting action",
      "sources": ["article_id#chunk_index"],
      "requires_approval": false
    }}
  ],
  "sources": ["article_id#chunk_index"],
  "escalation_recommended": false,
  "escalation_reason": null
}}

Additional rules:
- If sufficient_context is false:
  steps MUST be [].
  escalation_recommended MUST be true.
  escalation_reason MUST describe the missing documentation.
""".strip()


def _build_repair_prompt(
    *,
    original_response,
    validation_error,
):
    return f"""
Repair the following IT support resolution JSON.

Validation error:
{validation_error}

Return ONLY valid JSON.

Required fields:
- sufficient_context
- summary
- steps
- sources
- escalation_recommended
- escalation_reason

Do not introduce information that was not
present in the original response.

Original response:
{original_response}
""".strip()


def _refusal_response(reason):
    return {
        "sufficient_context": False,
        "summary": "",
        "steps": [],
        "sources": [],
        "escalation_recommended": True,
        "escalation_reason": reason,
        "steps_generated": 0,
        "steps_dropped": 0,
        "dropped_details": [],
        "confidence": 0.0,
        "confidence_parts": {
            "top_rerank": 0.0,
            "citation_coverage": 0.0,
            "classification": 0.0,
        },
        "confidence_label": "PROVISIONAL",
    }


def generate_resolution(
    *,
    subject,
    description,
    category="",
    subcategory="",
    already_tried="",
    severity="",
    packed_context="",
    retrieval_results=None,
    classification_confidence=0.0,
):
    """
    Complete M2 resolution-generation pipeline.

    Qwen3 generates the draft.
    Schema validation is applied.
    One repair attempt is allowed.
    Citation and destructive-action guardrails
    are applied after generation.
    """

    if not packed_context.strip():
        return _refusal_response(
            "No sufficient knowledge-base "
            "context was retrieved for this ticket."
        )

    prompt = _build_prompt(
        subject=subject,
        description=description,
        category=category,
        subcategory=subcategory,
        already_tried=already_tried,
        packed_context=packed_context,
    )

    raw_response = _call_ollama(
        prompt
    )

    try:
        resolution = _validate_resolution(
            _extract_json(
                raw_response
            )
        )

    except Exception as first_error:
        repair_prompt = _build_repair_prompt(
            original_response=raw_response,
            validation_error=str(
                first_error
            ),
        )

        try:
            repaired_response = _call_ollama(
                repair_prompt
            )

            resolution = _validate_resolution(
                _extract_json(
                    repaired_response
                )
            )

        except Exception:
            return _refusal_response(
                "The generated resolution "
                "could not be validated safely."
            )

    resolution = enforce_citations(
        resolution,
        packed_context,
    )

    resolution = (
        enforce_destructive_guardrail(
            resolution
        )
    )

    steps = (
        resolution.get("steps")
        or []
    )

    steps_with_valid_citations = sum(
        1
        for step in steps
        if step.get("sources")
    )

    total_steps = (
        resolution.get(
            "steps_generated",
            len(steps),
        )
    )

    top_rerank_score = 0.0

    if retrieval_results:
        top_rerank_score = max(
            float(
                result.get(
                    "rerank_score",
                    0.0,
                )
            )
            for result in retrieval_results
        )

    confidence = (
        calculate_provisional_confidence(
            top_rerank_score=top_rerank_score,
            steps_with_valid_citations=(
                steps_with_valid_citations
            ),
            total_steps=total_steps,
            classification_confidence=(
                classification_confidence
            ),
        )
    )

    resolution.update(
        confidence
    )

    return resolution