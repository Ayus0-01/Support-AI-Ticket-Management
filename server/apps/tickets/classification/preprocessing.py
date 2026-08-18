import re


MAX_TEXT_LENGTH = 6000


def remove_quoted_replies(text):
    """
    Remove common quoted email/reply sections.
    """

    if not text:
        return ""

    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:

        stripped = line.strip()

        # Lines beginning with > are quoted replies
        if stripped.startswith(">"):
            continue

        # Common email reply marker
        if re.match(r"^On .+ wrote:$", stripped, re.IGNORECASE):
            break

        # Original message separator
        if "-----Original Message-----" in stripped:
            break

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def remove_signature(text):
    """
    Remove common email signatures.
    """

    if not text:
        return ""

    patterns = [
        r"\nRegards,.*$",
        r"\nBest regards,.*$",
        r"\nKind regards,.*$",
        r"\nSent from my .*?$",
    ]

    cleaned = text

    for pattern in patterns:
        cleaned = re.sub(
            pattern,
            "",
            cleaned,
            flags=re.IGNORECASE | re.DOTALL
        )

    return cleaned.strip()


def mask_pii(text):
    """
    Mask common PII before classification.
    """

    if not text:
        return ""

    # Email addresses
    text = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "[EMAIL]",
        text
    )

    # IPv4 addresses
    text = re.sub(
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        "[IP]",
        text
    )

    # Phone numbers
    text = re.sub(
        r"\b(?:\+?\d[\d\s\-()]{8,}\d)\b",
        "[PHONE]",
        text
    )

    # Employee IDs such as EMP12345 or EMP-12345
    text = re.sub(
        r"\bEMP[- ]?\d{3,}\b",
        "[EMPLOYEE_ID]",
        text,
        flags=re.IGNORECASE
    )

    # Anything after "password is"
    text = re.sub(
        r"(password\s+is\s+)(.+)",
        r"\1[PASSWORD]",
        text,
        flags=re.IGNORECASE
    )

    return text


def truncate_text(text, max_length=MAX_TEXT_LENGTH):
    """
    Keep classification input within the configured text budget.
    """

    if not text:
        return ""

    return text[:max_length]


def preprocess_text(text):
    """
    Complete preprocessing pipeline for a single text field.
    """

    text = remove_quoted_replies(text)
    text = remove_signature(text)
    text = mask_pii(text)
    text = truncate_text(text)

    return text.strip()


def preprocess_ticket(subject, description):
    """
    Preprocess a ticket before feature extraction/classification.
    """

    return {
        "subject": preprocess_text(subject),
        "description": preprocess_text(description),
    }