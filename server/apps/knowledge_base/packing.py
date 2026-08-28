from datetime import datetime


def _format_updated_at(value):
    if isinstance(value, datetime):
        return value.isoformat()

    if value is None:
        return ""

    return str(value)


def _estimate_tokens(text):
    """
    Simple token-budget approximation for M2 context packing.
    """
    return max(
        1,
        len(text.split()),
    )


def pack_context(
    chunks,
    budget_tokens=4000,
):
    """
    Pack reranked KB chunks into a citation-ready
    context string.

    Chunks are expected to be ordered by rerank
    score descending before packing.
    """

    if not chunks:
        return ""

    packed_parts = []
    used_tokens = 0

    for chunk in chunks:
        article_id = chunk.get(
            "article_id"
        )

        chunk_index = chunk.get(
            "chunk_index"
        )

        title = chunk.get(
            "article_title",
            "",
        )

        heading_path = chunk.get(
            "heading_path",
            "",
        )

        updated_at = _format_updated_at(
            chunk.get(
                "article_updated_at"
            )
        )

        content = chunk.get(
            "content",
            "",
        ).strip()

        if not content:
            continue

        source_marker = (
            f"[SOURCE:{article_id}#{chunk_index}]"
        )

        block = "\n".join(
            [
                source_marker,
                f"Title: {title}",
                f"Section: {heading_path}",
                f"Updated: {updated_at}",
                "---",
                content,
            ]
        )

        block_tokens = _estimate_tokens(
            block
        )

        if (
            used_tokens + block_tokens
            > budget_tokens
        ):
            break

        packed_parts.append(
            block
        )

        used_tokens += block_tokens

    return "\n\n".join(
        packed_parts
    )