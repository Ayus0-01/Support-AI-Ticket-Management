import re


CATEGORY_KEYWORDS = {
    "vpn": [
        "vpn",
        "anyconnect",
        "remote access",
    ],
    "network": [
        "network",
        "internet",
        "wifi",
        "connect",
        "connectivity",
        "router",
    ],
    "hardware": [
        "laptop",
        "desktop",
        "keyboard",
        "mouse",
        "monitor",
        "printer",
        "hardware",
    ],
    "software": [
        "application",
        "software",
        "crash",
        "install",
        "installation",
        "error",
    ],
    "security": [
        "phishing",
        "malware",
        "virus",
        "suspicious",
        "breach",
        "unauthorized",
        "security",
    ],
}


def has_error_code(text):
    """
    Detect common technical error-code patterns.
    """

    if not text:
        return False

    patterns = [
        r"\bERR[-_ ]?\d+\b",
        r"\bERROR[-_ ]?\d+\b",
        r"\b0x[0-9A-Fa-f]+\b",
        r"\b\d{3,5}\b",
    ]

    return any(
        re.search(pattern, text, re.IGNORECASE)
        for pattern in patterns
    )


def extract_keyword_flags(text):
    """
    Detect useful classification keywords.
    """

    text = text.lower() if text else ""

    flags = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        flags[category] = any(
            keyword in text
            for keyword in keywords
        )

    flags["site_down"] = "site down" in text

    return flags


def extract_features(
    subject,
    description,
    department=None,
    channel=None,
    affected_scope=None,
    work_blocked=None,
):
    """
    Extract deterministic features from a preprocessed ticket.
    """

    subject = subject or ""
    description = description or ""

    combined_text = f"{subject} {description}"

    return {
        "subject": subject,
        "description": description,

        "department": department,
        "channel": channel,
        "affected_scope": affected_scope,
        "work_blocked": work_blocked,

        "has_error_code": has_error_code(combined_text),

        "keyword_flags": extract_keyword_flags(
            combined_text
        ),

        # Will be populated in the embedding stage.
        "embedding": None,
    }