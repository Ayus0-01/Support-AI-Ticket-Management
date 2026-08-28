from datetime import datetime, timezone

from bson import ObjectId

from AIticket.db import (
    article_chunks_collection,
    article_versions_collection,
    knowledge_articles_collection,
)

from apps.knowledge_base.services import (
    create_article_version,
)
from apps.knowledge_base.vectorstore import (
    upsert_chunks,
)


def main():
    article = knowledge_articles_collection.find_one(
        {
            "slug": "m2-vpn-publish-test"
        }
    )

    if not article:
        raise AssertionError(
            "M2 VPN publish test article not found."
        )

    article_id = article["_id"]

    before_article = knowledge_articles_collection.find_one(
        {
            "_id": article_id
        }
    )

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

    before_versions = list(
        article_versions_collection.find(
            {
                "article_id": article_id
            }
        ).sort(
            "version",
            1,
        )
    )

    client = (
        knowledge_articles_collection
        .database
        .client
    )

    print(
        "BEFORE:",
        {
            "status": before_article.get("status"),
            "chunk_count": len(before_chunks),
            "versions": len(before_versions),
        },
    )

    try:
        with client.start_session() as session:
            with session.start_transaction():

                # Deliberately create database changes.
                working_article = dict(
                    before_article
                )

                working_article["updated_at"] = (
                    datetime.now(
                        timezone.utc
                    )
                )

                working_article["status"] = (
                    "PUBLISHED"
                )

                actor_id = (
                    working_article.get(
                        "author_id"
                    )
                    or ObjectId()
                )

                actor_name = (
                    working_article.get(
                        "author_name"
                    )
                    or "Transaction Test"
                )

                create_article_version(
                    article=working_article,
                    changed_by_id=actor_id,
                    changed_by_name=actor_name,
                    change_note=(
                        "Intentional rollback test"
                    ),
                    session=session,
                )

                # This deliberately uses a valid copy of an
                # existing chunk so the transaction gets as far
                # as the actual chunk write.
                if not before_chunks:
                    raise AssertionError(
                        "Test article has no chunks."
                    )

                chunk = dict(
                    before_chunks[0]
                )

                chunk.pop(
                    "_id",
                    None,
                )

                chunk["chunk_index"] = 99

                upsert_chunks(
                    article_id=article_id,
                    article_title=before_article[
                        "title"
                    ],
                    article_status="PUBLISHED",
                    category=before_article[
                        "category"
                    ],
                    sub_category=before_article.get(
                        "sub_category",
                        "",
                    ),
                    article_slug=before_article.get(
                        "slug",
                        "",
                    ),
                    article_updated_at=working_article[
                        "updated_at"
                    ],
                    chunks=[
                        chunk
                    ],
                    replace_existing=False,
                    session=session,
                )

                # Intentional failure AFTER writes.
                raise RuntimeError(
                    "INTENTIONAL TRANSACTION ROLLBACK"
                )

    except RuntimeError as exc:
        assert str(exc) == (
            "INTENTIONAL TRANSACTION ROLLBACK"
        )
        print(
            "EXPECTED FAILURE:",
            str(exc),
        )

    after_article = knowledge_articles_collection.find_one(
        {
            "_id": article_id
        }
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

    after_versions = list(
        article_versions_collection.find(
            {
                "article_id": article_id
            }
        ).sort(
            "version",
            1,
        )
    )

    print(
        "AFTER:",
        {
            "status": after_article.get("status"),
            "chunk_count": len(after_chunks),
            "versions": len(after_versions),
        },
    )

    assert after_article == before_article

    assert (
        [
            (
                chunk["_id"],
                chunk.get("chunk_index"),
            )
            for chunk in after_chunks
        ]
        ==
        [
            (
                chunk["_id"],
                chunk.get("chunk_index"),
            )
            for chunk in before_chunks
        ]
    )

    assert (
        [
            version["_id"]
            for version in after_versions
        ]
        ==
        [
            version["_id"]
            for version in before_versions
        ]
    )

    print(
        "TRANSACTION ROLLBACK: PASS"
    )


if __name__ == "__main__":
    main()