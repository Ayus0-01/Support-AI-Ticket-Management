import re


DESTRUCTIVE_PATTERNS = {
    "DELETE": re.compile(
        r"\bdelete\b",
        re.IGNORECASE,
    ),
    "FORMAT": re.compile(
        r"\bformat\b",
        re.IGNORECASE,
    ),
    "RESET": re.compile(
        r"\breset\b",
        re.IGNORECASE,
    ),
    "UNINSTALL": re.compile(
        r"\buninstall\b",
        re.IGNORECASE,
    ),
    "REGEDIT": re.compile(
        r"\bregedit\b|\bregistry\b",
        re.IGNORECASE,
    ),
    "CREDENTIAL_CHANGE": re.compile(
        r"\bcredential(?:s)?\b"
        r"|\bchange\s+(?:your\s+)?password\b"
        r"|\breset\s+(?:your\s+)?password\b",
        re.IGNORECASE,
    ),
}


def detect_destructive_action(
    instruction,
):
    """
    Independently detect potentially destructive
    actions in a generated instruction.
    """

    instruction = instruction or ""

    matched = []

    for name, pattern in (
        DESTRUCTIVE_PATTERNS.items()
    ):
        if pattern.search(instruction):
            matched.append(name)

    return matched


def enforce_destructive_guardrail(
    resolution,
):
    """
    Model output cannot override the destructive-action
    guardrail.

    Any tagged step requires human approval.
    """

    updated = dict(resolution)

    steps = []

    for step in (
        resolution.get("steps")
        or []
    ):
        step_copy = dict(step)

        matches = detect_destructive_action(
            step_copy.get(
                "instruction",
                "",
            )
        )

        if matches:
            step_copy[
                "requires_approval"
            ] = True

            step_copy[
                "is_destructive"
            ] = True

            step_copy[
                "destructive_reason"
            ] = (
                "Detected potentially destructive "
                "action(s): "
                + ", ".join(matches)
            )

        else:
            step_copy.setdefault(
                "requires_approval",
                False,
            )

        steps.append(
            step_copy
        )

    updated["steps"] = steps

    return updated