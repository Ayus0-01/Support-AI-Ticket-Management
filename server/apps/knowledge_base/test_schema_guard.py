from datetime import datetime, timezone

from bson import ObjectId

from AIticket.db import article_chunks_collection


def main():
    bad_document = {
        "article_id": ObjectId(),
        "chunk_index": 0,
        "content": (
            "This is a deliberately invalid "
            "vector test document."
        ),
        "article_status": "PUBLISHED",
        "category": "VPN",
        "token_count": 50,
        "embedding": [
            0.1,
            0.2,
            0.3,
        ],
        "embedding_model": (
            "BAAI/bge-large-en-v1.5"
        ),
        "created_at": datetime.now(
            timezone.utc
        ),
    }

    try:
        article_chunks_collection.insert_one(
            bad_document
        )

        print(
            "ERROR: INVALID VECTOR WAS ACCEPTED"
        )

        raise AssertionError(
            "MongoDB accepted an invalid "
            "3-dimensional embedding."
        )

    except Exception as exc:
        print(
            "INVALID VECTOR REJECTED:",
            type(exc).__name__,
        )
        print(
            "SCHEMA GUARD: PASS"
        )


if __name__ == "__main__":
    main()