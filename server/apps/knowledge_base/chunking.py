import re
from typing import Dict, List, Optional


# M2 storage/retrieval constraints and targets.
MIN_CHUNK_TOKENS = 50
TARGET_MIN_TOKENS = 500
TARGET_MAX_TOKENS = 800
OVERLAP_RATIO = 0.15
PRIMARY_HEADING_MAX_LEVEL = 3


def estimate_tokens(text: str) -> int:
    """Deterministic lightweight token estimate."""
    if not text:
        return 0

    return len(
        re.findall(
            r"\S+",
            text,
        )
    )


def _heading_level(line: str) -> Optional[int]:
    match = re.match(
        r"^(#{1,6})\s+(.+?)\s*$",
        line.strip(),
    )

    if not match:
        return None

    return len(match.group(1))


def _heading_text(line: str) -> str:
    match = re.match(
        r"^#{1,6}\s+(.+?)\s*$",
        line.strip(),
    )

    if not match:
        return ""

    return match.group(1).strip()


def _heading_prefix(heading_path: List[str]) -> str:
    if not heading_path:
        return ""

    return " > ".join(
        heading.strip()
        for heading in heading_path
        if heading and heading.strip()
    )


def _update_heading_stack(
    stack: List[str],
    level: int,
    heading: str,
) -> List[str]:
    """Update the H1-H3 semantic heading hierarchy."""
    if level > PRIMARY_HEADING_MAX_LEVEL:
        return list(stack)

    updated = list(stack)[: level - 1]
    updated.append(heading)
    return updated


def _build_sections(text: str) -> List[Dict]:
    """
    Split a normalized document using H1-H3 semantic boundaries.

    The heading itself is not duplicated into normal section content;
    heading_path is stored separately and is prepended once at the end.
    """
    if not text or not text.strip():
        return []

    sections: List[Dict] = []
    current_heading_stack: List[str] = []
    current_lines: List[str] = []

    def flush() -> None:
        nonlocal current_lines

        content = "\n".join(current_lines).strip()

        if content:
            sections.append(
                {
                    "heading_path": list(current_heading_stack),
                    "text": content,
                }
            )

        current_lines = []

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line:
            if current_lines:
                current_lines.append("")
            continue

        level = _heading_level(line)

        if (
            level is not None
            and level <= PRIMARY_HEADING_MAX_LEVEL
        ):
            flush()

            heading = _heading_text(line)
            if not heading:
                continue

            current_heading_stack = _update_heading_stack(
                current_heading_stack,
                level,
                heading,
            )
            continue

        # Normal content and H4-H6 remain inside the current H1-H3 section.
        current_lines.append(line)

    flush()
    return sections


def _is_direct_child(
    parent_path: List[str],
    child_path: List[str],
) -> bool:
    return (
        len(child_path) == len(parent_path) + 1
        and child_path[:-1] == parent_path
    )


def _merge_small_sections(
    sections: List[Dict],
) -> List[Dict]:
    """
    Prevent semantically tiny H1-H3 sections from becoming invalid
    article_chunks documents.

    M2's MongoDB validator requires token_count >= 50. When a small
    child section is encountered, fold it into its immediate parent
    while retaining the child heading as labelled content.

    This preserves the information while preventing a tiny child
    subsection from becoming an unsearchable/invalid standalone chunk.
    """
    if not sections:
        return []

    result: List[Dict] = []

    for section in sections:
        heading_path = list(section.get("heading_path", []))
        content = (section.get("text", "") or "").strip()

        if not content:
            continue

        section_tokens = estimate_tokens(content)

        if section_tokens >= MIN_CHUNK_TOKENS or not result:
            result.append(
                {
                    "heading_path": heading_path,
                    "text": content,
                }
            )
            continue

        previous = result[-1]
        previous_path = list(
            previous.get("heading_path", [])
        )

        # M2 allows tiny fragments created by heading splits to be merged.
        # Prefer their direct parent, but when no safe parent exists, merge
        # the tiny fragment into the immediately preceding section provided
        # the resulting stored chunk remains within the 800-token ceiling.
        child_heading = heading_path[-1] if heading_path else "Section"

        merged_content = (
            previous["text"]
            + "\n\n"
            + child_heading
            + "\n"
            + content
        ).strip()

        final_tokens = estimate_tokens(
            _prepend_heading_path(
                merged_content,
                previous_path,
            )
        )

        if final_tokens <= TARGET_MAX_TOKENS:
            previous["text"] = merged_content
            continue

        # If a tiny section cannot be merged safely, retain it. The final
        # validation will raise a clear error rather than corrupting content.
        result.append(
            {
                "heading_path": heading_path,
                "text": content,
            }
        )

    return result


def _split_long_section(
    text: str,
    heading_path: List[str],
) -> List[Dict]:
    """
    Split long semantic sections into <=800-token final chunks,
    reserving space for the prepended heading path and using ~15%
    overlap.
    """
    words = text.split()

    if not words:
        return []

    heading_tokens = estimate_tokens(
        _heading_prefix(heading_path)
    )

    content_budget = max(
        1,
        TARGET_MAX_TOKENS - heading_tokens,
    )

    if len(words) <= content_budget:
        return [
            {
                "heading_path": list(heading_path),
                "content": text.strip(),
            }
        ]

    overlap_tokens = max(
        1,
        int(content_budget * OVERLAP_RATIO),
    )

    chunks: List[Dict] = []
    start = 0

    while start < len(words):
        end = min(
            start + content_budget,
            len(words),
        )

        content = " ".join(words[start:end]).strip()

        if content:
            chunks.append(
                {
                    "heading_path": list(heading_path),
                    "content": content,
                }
            )

        if end >= len(words):
            break

        next_start = max(
            end - overlap_tokens,
            start + 1,
        )
        start = next_start

    return chunks


def _prepend_heading_path(
    content: str,
    heading_path: List[str],
) -> str:
    prefix = _heading_prefix(heading_path)

    if not prefix:
        return content.strip()

    return (
        prefix
        + "\n"
        + content.strip()
    ).strip()


def _merge_small_chunks(
    chunks: List[Dict],
) -> List[Dict]:
    """
    Merge tiny adjacent chunks only when the same heading path is
    preserved and the final stored chunk stays within the M2 maximum.
    """
    if not chunks:
        return []

    result: List[Dict] = []

    for chunk in chunks:
        content = (chunk.get("content", "") or "").strip()
        heading_path = list(chunk.get("heading_path", []) or [])

        if not content:
            continue

        if not result:
            result.append(
                {
                    "heading_path": heading_path,
                    "content": content,
                }
            )
            continue

        current_tokens = estimate_tokens(content)
        previous = result[-1]
        previous_path = list(previous.get("heading_path", []))

        if (
            current_tokens < MIN_CHUNK_TOKENS
            and previous_path == heading_path
        ):
            combined = (
                previous["content"]
                + "\n\n"
                + content
            )

            if (
                estimate_tokens(
                    _prepend_heading_path(
                        combined,
                        heading_path,
                    )
                )
                <= TARGET_MAX_TOKENS
            ):
                previous["content"] = combined
                continue

        result.append(
            {
                "heading_path": heading_path,
                "content": content,
            }
        )

    return result


def _validate_final_chunks(
    chunks: List[Dict],
) -> None:
    for chunk in chunks:
        token_count = chunk["token_count"]

        if token_count < MIN_CHUNK_TOKENS:
            raise ValueError(
                "Chunk is below the M2 minimum token count: "
                f"{token_count} < {MIN_CHUNK_TOKENS}. "
                "The section could not be merged safely."
            )

        if token_count > TARGET_MAX_TOKENS:
            raise ValueError(
                "Chunk exceeds the M2 maximum token count: "
                f"{token_count} > {TARGET_MAX_TOKENS}."
            )


def chunk_document(
    document: Dict,
) -> List[Dict]:
    """
    Convert a normalized document into M2 retrieval chunks.

    Guarantees:
        - H1-H3 heading-aware semantic sections
        - small child sections merged into their parent when needed
        - final token_count in 50..800
        - ~15% overlap for long sections
        - heading path prepended exactly once
        - sequential chunk_index values
    """
    if not isinstance(document, dict):
        raise TypeError(
            "document must be a dict"
        )

    normalized_text = (
        document.get("text", "") or ""
    ).strip()

    if not normalized_text:
        return []

    sections = _build_sections(
        normalized_text
    )

    sections = _merge_small_sections(
        sections
    )

    raw_chunks: List[Dict] = []

    for section in sections:
        content = (
            section.get("text", "") or ""
        ).strip()

        if not content:
            continue

        raw_chunks.extend(
            _split_long_section(
                content,
                list(section.get("heading_path", [])),
            )
        )

    raw_chunks = _merge_small_chunks(
        raw_chunks
    )

    final_chunks: List[Dict] = []

    for raw_chunk in raw_chunks:
        heading_path = list(
            raw_chunk.get("heading_path", [])
        )
        content = (
            raw_chunk.get("content", "") or ""
        ).strip()

        if not content:
            continue

        final_content = _prepend_heading_path(
            content,
            heading_path,
        )

        final_chunks.append(
            {
                "chunk_index": len(final_chunks),
                "heading_path": _heading_prefix(
                    heading_path
                ),
                "content": final_content,
                "token_count": estimate_tokens(
                    final_content
                ),
            }
        )

    _validate_final_chunks(
        final_chunks
    )

    return final_chunks