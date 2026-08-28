from bson import ObjectId

from AIticket.db import article_chunks_collection
from apps.knowledge_base.services import (
    create_knowledge_article,
    publish_knowledge_article,
)


def main():
    article_text = """
# VPN Troubleshooting

## Timeout Errors

When a VPN connection times out, first verify that the device has
working network connectivity. Confirm that the VPN client is connected
to the correct server address and that the configured gateway is
reachable. Check whether the organization firewall permits the required
VPN traffic and verify that the client configuration matches the
approved settings.

### Client Configuration

Verify the VPN server address, authentication settings, protocol
configuration, and any required certificates. Clear stale cached
credentials when appropriate and restart the VPN client before testing
the connection again.

## Escalation

If the documented troubleshooting steps do not resolve the timeout,
collect the client logs and connection details and escalate the issue
to the appropriate support team.
""".strip()

    author_id = ObjectId()

    article = create_knowledge_article(
        title="M2 VPN Publish Test",
        slug="m2-vpn-publish-test",
        category="VPN",
        sub_category="Connection failure",
        tags=[
            "vpn",
            "timeout",
        ],
        content=article_text,
        author_id=author_id,
        author_name="M2 Test",
    )

    published = publish_knowledge_article(
        article_id=article["_id"]
    )

    print(
        "ARTICLE:",
        {
            "id": str(
                published["_id"]
            ),
            "status": published.get(
                "status"
            ),
            "version": published.get(
                "version"
            ),
            "indexed_version": published.get(
                "indexed_version"
            ),
            "chunk_count": published.get(
                "chunk_count"
            ),
            "embedding_model": published.get(
                "embedding_model"
            ),
            "index_error": published.get(
                "index_error"
            ),
        },
    )

    chunks = list(
        article_chunks_collection.find(
            {
                "article_id": published[
                    "_id"
                ]
            }
        ).sort(
            "chunk_index",
            1,
        )
    )

    print(
        "CHUNKS:",
        len(chunks),
    )

    for chunk in chunks:
        print(
            {
                "index": chunk.get(
                    "chunk_index"
                ),
                "tokens": chunk.get(
                    "token_count"
                ),
                "heading_path": chunk.get(
                    "heading_path"
                ),
                "dim": len(
                    chunk.get(
                        "embedding",
                        [],
                    )
                ),
                "model": chunk.get(
                    "embedding_model"
                ),
                "status": chunk.get(
                    "article_status"
                ),
            }
        )

    assert published.get(
        "status"
    ) == "PUBLISHED"

    assert (
        published.get(
            "indexed_version"
        )
        == published.get(
            "version"
        )
    )

    assert published.get(
        "index_error"
    ) is None

    assert chunks

    assert all(
        len(
            chunk.get(
                "embedding",
                [],
            )
        )
        == 1024
        for chunk in chunks
    )

    assert all(
        chunk.get(
            "heading_path"
        )
        for chunk in chunks
    )

    assert all(
        chunk.get(
            "article_status"
        )
        == "PUBLISHED"
        for chunk in chunks
    )

    assert all(
        chunk.get(
            "token_count",
            0,
        )
        >= 50
        for chunk in chunks
    )

    print(
        "CANONICAL PUBLISH/INDEX: PASS"
    )


if __name__ == "__main__":
    main()