import re


SOURCE_PATTERN = re.compile(
    r"\[SOURCE:([^#\]]+)#(\d+)\]"
)


def extract_valid_source_ids(packed_context):
    """
    Extract the exact SOURCE markers that were actually
    supplied to the model.
    """

    if not packed_context:
        return set()

    return {
        match.group(0)
        for match in SOURCE_PATTERN.finditer(
            packed_context
        )
    }


def normalize_source(source):
    """
    Accept:
        [SOURCE:article#3]
        article#3

    and normalize to:
        [SOURCE:article#3]
    """

    if not isinstance(source, str):
        return None

    source = source.strip()

    if source.startswith("[SOURCE:") and source.endswith("]"):
        return source

    match = re.fullmatch(
        r"([^#\[\]]+)#(\d+)",
        source,
    )

    if not match:
        return None

    return (
        f"[SOURCE:{match.group(1)}#"
        f"{match.group(2)}]"
    )


def enforce_citations(
    resolution,
    packed_context,
):
    """
    Drop any generated step that has no valid citation.

    A citation is valid only when its SOURCE marker
    exists in the context actually supplied to Qwen.
    """

    valid_sources = extract_valid_source_ids(
        packed_context
    )

    updated = dict(resolution)

    original_steps = (
        resolution.get("steps")
        or []
    )

    kept_steps = []
    dropped_details = []

    for index, step in enumerate(
        original_steps,
        start=1,
    ):
        step_copy = dict(step)

        normalized_sources = []

        for source in (
            step.get("sources")
            or []
        ):
            normalized = normalize_source(
                source
            )

            if (
                normalized
                and normalized in valid_sources
            ):
                normalized_sources.append(
                    normalized
                )

        if not normalized_sources:
            dropped_details.append(
                {
                    "instruction": step.get(
                        "instruction",
                        "",
                    ),
                    "reason": "NO_VALID_CITATION",
                }
            )
            continue

        step_copy["sources"] = (
            normalized_sources
        )

        if not step_copy.get("order"):
            step_copy["order"] = index

        kept_steps.append(
            step_copy
        )

    updated["steps_generated"] = len(
        original_steps
    )

    updated["steps_dropped"] = len(
        dropped_details
    )

    updated["dropped_details"] = (
        dropped_details
    )

    updated["steps"] = kept_steps

    if not kept_steps and original_steps:
        updated["sufficient_context"] = False
        updated["escalation_recommended"] = True

        if not updated.get(
            "escalation_reason"
        ):
            updated[
                "escalation_reason"
            ] = (
                "All generated steps were "
                "discarded because they lacked "
                "valid knowledge-base citations."
            )

    return updated