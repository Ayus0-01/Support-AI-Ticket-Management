from __future__ import annotations

import json
import urllib.request


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen3:4b"

MIN_QUERY_WORDS = 4
MAX_QUERY_WORDS = 10

MAX_RETRIES = 1

REQUEST_TIMEOUT = 300


def _call_ollama(
    prompt: str,
) -> str:
    """
    Call the local Ollama model and return
    the raw JSON response string.
    """

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "think": False,
        "format": {
            "type": "object",
            "properties": {
                "queries": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "minItems": 2,
                    "maxItems": 3,
                }
            },
            "required": [
                "queries"
            ],
        },
        "options": {
            "temperature": 0.1,
            "num_predict": 256,
        },
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(
            payload
        ).encode("utf-8"),
        headers={
            "Content-Type": "application/json"
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=REQUEST_TIMEOUT,
    ) as response:
        result = json.loads(
            response.read().decode("utf-8")
        )

    return result["response"]


def _validate_queries(
    queries,
) -> list[str]:
    """
    Validate and normalize LLM-generated queries.

    Each accepted query must contain between
    MIN_QUERY_WORDS and MAX_QUERY_WORDS words.
    """

    if not isinstance(
        queries,
        list,
    ):
        return []

    valid_queries = []

    for query in queries:
        query = str(
            query
        ).strip()

        if not query:
            continue

        word_count = len(
            query.split()
        )

        if (
            MIN_QUERY_WORDS
            <= word_count
            <= MAX_QUERY_WORDS
        ):
            if query not in valid_queries:
                valid_queries.append(
                    query
                )

    return valid_queries[:3]

def _build_preservation_query(
    *,
    subject: str,
    description: str,
    category: str,
    affected_system: str,
) -> str:
    """
    Build one deterministic query that preserves important
    ticket-specific context.

    For EMAIL tickets, preserve distinctions such as:
        - outgoing vs incoming
        - delivery failure
        - distribution list
        - spam/junk
        - mailbox synchronization
        - calendar synchronization
        - storage quota
    """

    if category.upper() == "EMAIL":
        text = (
            f"{subject} "
            f"{description}"
        ).lower()

        parts = [
            "email",
        ]

        if (
            "outgoing" in text
            or "sent" in text
        ):
            parts.append(
                "outgoing message"
            )

        if (
            "delivery failure" in text
            or "not delivered" in text
            or "non-delivery" in text
            or "bounce" in text
        ):
            if "distribution list" in text:
                parts.append(
                    "distribution list delivery"
                )

            else:
                parts.append(
                    "specific recipient delivery failure"
                )

        if "distribution list" in text:
            parts.append(
                "distribution list"
            )

        if (
            "spam" in text
            or "junk" in text
        ):
            parts.append(
                "spam filtering"
            )

        if "calendar" in text:
            parts.append(
                "calendar synchronization"
            )

        if "quota" in text or "storage" in text:
            parts.append(
                "mailbox storage quota"
            )

        if "synchroniz" in text:
            parts.append(
                "mailbox synchronization"
            )

        query = " ".join(parts)

    else:
        query = " ".join(
            part.strip()
            for part in [
                category,
                affected_system,
                subject,
            ]
            if part and part.strip()
        )

    words = query.split()

    if len(words) > MAX_QUERY_WORDS:
        query = " ".join(
            words[:MAX_QUERY_WORDS]
        )

    return query.strip()

def _build_prompt(
    *,
    subject: str,
    description: str,
    category: str,
    affected_system: str,
    strict: bool = False,
) -> str:
    """
    Build the query-generation prompt.

    The prompt must preserve information actually present
    in the ticket and must not invent technical details.
    """

    base_rules = (
        "Extract 2 to 3 focused IT support search queries "
        "from the ticket below.\n"
        "Each query must contain 4 to 10 words.\n"
        "Use only information supported by the ticket.\n"
        "Do not invent symptoms, causes, applications, devices, "
        "services, errors, or technical details.\n"
        "Preserve the actual problem described by the requester.\n"
    )

    ambiguity_rules = (
        "If the ticket is vague and does not identify the "
        "affected service, system, device, or application, "
        "keep the queries general.\n"
        "For vague requests, emphasize clarification, missing "
        "information, affected-service identification, or "
        "general support rather than inventing a technical "
        "problem.\n"
    )

    email_rules = ""

    if category.upper() == "EMAIL":
        email_rules = (
            "For EMAIL tickets, preserve the specific email "
            "problem type stated in the ticket.\n"
            "Distinguish outgoing versus incoming messages, "
            "delivery failures versus spam or junk filtering, "
            "ordinary recipients versus distribution lists, "
            "mailbox synchronization, calendar synchronization, "
            "and storage quota issues.\n"
            "When the ticket describes a message sent to a "
            "normal or specific recipient, include that "
            "recipient or delivery context in the query.\n"
            "Do not assume or introduce a distribution list "
            "unless the ticket explicitly mentions one.\n"
        )

    if strict:
        instruction = (
            "Generate exactly 2 or 3 search queries.\n"
            "EVERY SINGLE QUERY MUST CONTAIN AT LEAST 4 "
            "WORDS AND AT MOST 10 WORDS.\n"
            "Do NOT return 1-word, 2-word, or 3-word queries.\n"
            "Do NOT invent technical details not present "
            "in the ticket.\n"
            "Return only JSON matching the schema."
        )
    else:
        instruction = (
            "Return only JSON matching the schema."
        )

    return (
        base_rules
        + ambiguity_rules
        + email_rules
        + instruction
        + "\n\n"
        + f"Subject: {subject}\n"
        + f"Description: {description}\n"
        + f"Category: {category}\n"
        + f"Affected system: {affected_system}\n"
    )


def _fallback_queries(
    *,
    subject: str,
    description: str,
    category: str,
    affected_system: str,
) -> list[str]:
    """
    Deterministically generate safe fallback search queries.

    These are used only when the LLM response cannot
    produce valid 4-10 word queries.
    """

    candidates = [
        (
            f"{category} "
            f"{affected_system} "
            f"{subject}"
        ),
        (
            f"{affected_system} "
            f"{subject} "
            f"troubleshooting"
        ),
        (
            f"{category} "
            f"issue "
            f"{description}"
        ),
    ]

    valid_queries = []

    for candidate in candidates:
        words = candidate.split()

        # Keep the strongest portion within the allowed limit.
        if len(words) > MAX_QUERY_WORDS:
            candidate = " ".join(
                words[:MAX_QUERY_WORDS]
            )

        word_count = len(
            candidate.split()
        )

        if (
            MIN_QUERY_WORDS
            <= word_count
            <= MAX_QUERY_WORDS
        ):
            if candidate not in valid_queries:
                valid_queries.append(
                    candidate
                )

    # Guaranteed ticket-aware fallbacks for very
    # short/odd inputs.
    if not valid_queries:
        generic_candidates = [
            "IT issue troubleshooting request",
            "corporate technical support issue",
            "affected system troubleshooting problem",
        ]

        valid_queries = [
            query
            for query in generic_candidates
            if MIN_QUERY_WORDS
            <= len(query.split())
            <= MAX_QUERY_WORDS
        ]

    return valid_queries[:3]


def _generate_valid_queries(
    *,
    subject: str,
    description: str,
    category: str,
    affected_system: str,
) -> list[str]:
    """
    Try normal generation first, then retry once
    with a stricter prompt.

    Returns an empty list only when both attempts
    fail validation.
    """

    prompts = [
        _build_prompt(
            subject=subject,
            description=description,
            category=category,
            affected_system=affected_system,
            strict=False,
        )
    ]

    for _ in range(
        MAX_RETRIES
    ):
        prompts.append(
            _build_prompt(
                subject=subject,
                description=description,
                category=category,
                affected_system=affected_system,
                strict=True,
            )
        )

    for prompt in prompts:
        try:
            raw_response = _call_ollama(
                prompt
            )

            data = json.loads(
                raw_response
            )

            queries = _validate_queries(
                data.get(
                    "queries",
                    [],
                )
            )

            if queries:
                return queries

        except (
            json.JSONDecodeError,
            KeyError,
            TypeError,
            ValueError,
            urllib.error.URLError,
            TimeoutError,
        ):
            continue

    return []


def build_search_queries(
    *,
    subject: str,
    description: str,
    category: str = "",
    affected_system: str = "",
) -> list[str]:
    """
    Build search queries for a support ticket.

    Strategy:

        LLM generation
             ↓
        validation
             ↓
        one strict retry
             ↓
        deterministic fallback

    The function always returns at least one valid
    query unless the ticket fields themselves are
    unusable.
    """

    subject = (
        subject or ""
    ).strip()

    description = (
        description or ""
    ).strip()

    category = (
        category or ""
    ).strip()

    affected_system = (
        affected_system or ""
    ).strip()

    queries = _generate_valid_queries(
        subject=subject,
        description=description,
        category=category,
        affected_system=affected_system,
    )

    preservation_query = _build_preservation_query(
        subject=subject,
        description=description,
        category=category,
        affected_system=affected_system,
    )

    if preservation_query:
        queries = [
            preservation_query,
            *queries,
        ]

        deduplicated = []

        for query in queries:
            if query not in deduplicated:
                deduplicated.append(query)

        queries = deduplicated[:3]

    if queries:
        return queries

    fallback = _fallback_queries(
        subject=subject,
        description=description,
        category=category,
        affected_system=affected_system,
    )

    if fallback:
        return fallback

    raise ValueError(
        "Unable to generate valid search queries."
    )