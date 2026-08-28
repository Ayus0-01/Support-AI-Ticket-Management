def calculate_provisional_confidence(
    *,
    top_rerank_score,
    steps_with_valid_citations,
    total_steps,
    classification_confidence,
):
    """
    M2 provisional confidence.

    Formula:
        0.50 * top rerank score
        + 0.30 * citation coverage
        + 0.20 * classification confidence
    """

    if total_steps > 0:
        citation_coverage = (
            steps_with_valid_citations
            / total_steps
        )
    else:
        citation_coverage = 0.0

    confidence = (
        0.50 * max(
            0.0,
            min(
                1.0,
                float(
                    top_rerank_score
                ),
            ),
        )
        + 0.30 * max(
            0.0,
            min(
                1.0,
                float(
                    citation_coverage
                ),
            ),
        )
        + 0.20 * max(
            0.0,
            min(
                1.0,
                float(
                    classification_confidence
                ),
            ),
        )
    )

    return {
        "confidence": round(
            confidence,
            4,
        ),
        "confidence_parts": {
            "top_rerank": round(
                float(
                    top_rerank_score
                ),
                4,
            ),
            "citation_coverage": round(
                citation_coverage,
                4,
            ),
            "classification": round(
                float(
                    classification_confidence
                ),
                4,
            ),
        },
        "confidence_label": "PROVISIONAL",
    }