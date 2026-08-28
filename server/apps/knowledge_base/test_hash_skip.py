from AIticket.db import (
    article_chunks_collection,
    knowledge_articles_collection,
)

from apps.knowledge_base.services import (
    publish_knowledge_article,
)


def main():
    article = (
        knowledge_articles_collection.find_one(
            {
                "slug": "m2-vpn-publish-test"
            }
        )
    )

    if not article:
        raise AssertionError(
            "M2 publish test article not found."
        )

    article_id = article["_id"]

    before_article = dict(article)

    before_chunks = list(
        article_chunks_collection.find(
            {
                "article_id": article_id
            }
        ).sort(
            "chunk_index",
            1,
        )
    )

    if not before_chunks:
        raise AssertionError(
            "No indexed chunks found before hash-skip test."
        )

    before_chunk_ids = [
        chunk["_id"]
        for chunk in before_chunks
    ]

    before_hash = before_article.get(
        "content_hash"
    )

    before_indexed_version = (
        before_article.get(
            "indexed_version"
        )
    )

    before_model = (
        before_article.get(
            "embedding_model"
        )
    )

    republished = (
        publish_knowledge_article(
            article_id=article_id
        )
    )

    after_chunks = list(
        article_chunks_collection.find(
            {
                "article_id": article_id
            }
        ).sort(
            "chunk_index",
            1,
        )
    )

    after_chunk_ids = [
        chunk["_id"]
        for chunk in after_chunks
    ]

    print(
        "BEFORE:",
        {
            "hash": before_hash,
            "indexed_version": before_indexed_version,
            "model": before_model,
            "chunks": len(before_chunks),
        },
    )

    print(
        "AFTER:",
        {
            "hash": republished.get(
                "content_hash"
            ),
            "indexed_version": republished.get(
                "indexed_version"
            ),
            "model": republished.get(
                "embedding_model"
            ),
            "chunks": len(after_chunks),
        },
    )

    print(
        "CHUNK IDS UNCHANGED:",
        before_chunk_ids
        == after_chunk_ids,
    )

    assert (
        republished.get(
            "content_hash"
        )
        == before_hash
    )

    assert (
        republished.get(
            "indexed_version"
        )
        == before_indexed_version
    )

    assert (
        republished.get(
            "embedding_model"
        )
        == before_model
    )

    assert (
        before_chunk_ids
        == after_chunk_ids
    )

    print(
        "HASH SKIP / NO RE-EMBED: PASS"
    )


if __name__ == "__main__":
    main()