from apps.knowledge_base.normalization import (
    normalize_document,
)

from apps.knowledge_base.chunking import (
    chunk_document,
    estimate_tokens,
    TARGET_MAX_TOKENS,
    OVERLAP_RATIO,
)


def _content_without_heading_path(
    chunk,
):
    """
    Remove the prepended heading-path line so that
    overlap is measured only across actual content.
    """

    lines = chunk["content"].splitlines()

    if not lines:
        return ""

    heading_path = chunk.get(
        "heading_path",
        "",
    )

    if (
        heading_path
        and lines[0].strip()
        == heading_path.strip()
    ):
        return "\n".join(
            lines[1:]
        ).strip()

    return chunk["content"].strip()


def main():
    # -------------------------------------------------
    # Small semantic-document test
    # -------------------------------------------------

    document = {
        "title": "VPN Troubleshooting",
        "text": """
# VPN Troubleshooting

## Timeout Errors

Verify network connectivity.

### Client Configuration

Verify the VPN server configuration.

## Escalation

Contact the support team when troubleshooting fails.
""",
        "headings": [],
        "source_url": None,
        "source_updated_at": None,
    }

    normalized = normalize_document(
        document
    )

    chunks = chunk_document(
        normalized
    )

    assert chunks

    assert all(
        "chunk_index" in chunk
        for chunk in chunks
    )

    assert all(
        "heading_path" in chunk
        for chunk in chunks
    )

    assert all(
        "token_count" in chunk
        for chunk in chunks
    )

    combined = "\n".join(
        chunk["content"]
        for chunk in chunks
    )

    assert (
        "VPN Troubleshooting"
        in combined
    )

    assert (
        "Timeout Errors"
        in combined
    )

    assert (
        "Client Configuration"
        in combined
    )

    print(
        "NORMALIZATION: PASS"
    )

    print(
        "CHUNK COUNT:",
        len(chunks),
    )

    for chunk in chunks:
        print(
            {
                "index": chunk[
                    "chunk_index"
                ],
                "heading_path": chunk[
                    "heading_path"
                ],
                "tokens": chunk[
                    "token_count"
                ],
            }
        )

    print(
        "CHUNKING: PASS"
    )

    # -------------------------------------------------
    # Long-document test
    # -------------------------------------------------

    repeated_text = (
        "Verify network connectivity and VPN configuration "
        "before proceeding with additional troubleshooting. "
    ) * 250

    large_document = normalize_document(
        {
            "title": "Large VPN Guide",
            "text": (
                "# Large VPN Guide\n\n"
                "## Timeout Troubleshooting\n\n"
                + repeated_text
            ),
            "headings": [],
            "source_url": None,
            "source_updated_at": None,
        }
    )

    large_chunks = chunk_document(
        large_document
    )

    assert len(
        large_chunks
    ) > 1

    # Every final chunk must stay within
    # the M2 maximum.
    assert all(
        chunk["token_count"]
        <= TARGET_MAX_TOKENS
        for chunk in large_chunks
    )

    # All chunks from this semantic section
    # must retain the same heading path.
    assert all(
        chunk["heading_path"]
        == (
            "Large VPN Guide > "
            "Timeout Troubleshooting"
        )
        for chunk in large_chunks
    )

    # Chunk indexes must be sequential.
    assert [
        chunk["chunk_index"]
        for chunk in large_chunks
    ] == list(
        range(
            len(large_chunks)
        )
    )

    print(
        "LONG-DOCUMENT CHUNKING: PASS"
    )

    print(
        "LONG CHUNK COUNT:",
        len(large_chunks),
    )

    for chunk in large_chunks:
        print(
            {
                "index": chunk[
                    "chunk_index"
                ],
                "heading_path": chunk[
                    "heading_path"
                ],
                "tokens": chunk[
                    "token_count"
                ],
            }
        )

    # -------------------------------------------------
    # Explicit overlap test
    # -------------------------------------------------

    for index in range(
        len(large_chunks) - 1
    ):
        current_content = (
            _content_without_heading_path(
                large_chunks[index]
            )
        )

        next_content = (
            _content_without_heading_path(
                large_chunks[index + 1]
            )
        )

        current_words = (
            current_content.split()
        )

        next_words = (
            next_content.split()
        )

        assert current_words
        assert next_words

        heading_tokens = estimate_tokens(
            large_chunks[index][
                "heading_path"
            ]
        )

        content_budget = (
            TARGET_MAX_TOKENS
            - heading_tokens
        )

        expected_overlap = max(
            1,
            int(
                content_budget
                * OVERLAP_RATIO
            ),
        )

        assert len(
            current_words
        ) >= expected_overlap

        assert len(
            next_words
        ) >= expected_overlap

        current_tail = current_words[
            -expected_overlap:
        ]

        next_head = next_words[
            :expected_overlap
        ]

        assert (
            current_tail
            == next_head
        ), (
            "Expected approximately "
            f"{expected_overlap} overlapping "
            "tokens between chunks "
            f"{index} and {index + 1}."
        )

        print(
            "OVERLAP:",
            {
                "between": (
                    f"{index} -> "
                    f"{index + 1}"
                ),
                "expected_tokens": (
                    expected_overlap
                ),
                "verified": True,
            },
        )

    print(
        "OVERLAP VALIDATION: PASS"
    )


if __name__ == "__main__":
    main()