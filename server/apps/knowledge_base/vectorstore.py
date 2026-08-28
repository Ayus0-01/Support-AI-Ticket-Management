from datetime import datetime, timezone
from typing import Dict, List, Sequence

from bson import ObjectId
from pymongo import UpdateOne

from AIticket.db import article_chunks_collection

from .embeddings import EMBEDDING_DIM, MODEL_NAME, validate_embedding


VECTOR_INDEX_NAME = "kb_vector_index"
TEXT_INDEX_NAME = "kb_text_index"


def _to_object_id(value) -> ObjectId:
    if isinstance(value, ObjectId):
        return value
    try:
        return ObjectId(str(value))
    except Exception as exc:
        raise ValueError(f"Invalid ObjectId: {value}") from exc


def _utc_now():
    return datetime.now(timezone.utc)


def prepare_chunk_document(
    *,
    article_id,
    article_title: str,
    article_status: str,
    category: str,
    sub_category: str = "",
    article_slug: str = "",
    article_updated_at=None,
    chunk: Dict,
) -> Dict:
    if not article_title:
        raise ValueError("article_title is required.")

    if article_status not in {"DRAFT", "PUBLISHED", "ARCHIVED"}:
        raise ValueError(
            "article_status must be DRAFT, PUBLISHED or ARCHIVED."
        )

    if not category:
        raise ValueError("category is required.")

    if not isinstance(chunk, dict):
        raise TypeError("chunk must be a dictionary.")

    content = (chunk.get("content", "") or "").strip()
    if not content:
        raise ValueError("Chunk content cannot be empty.")

    chunk_index = chunk.get("chunk_index")
    if not isinstance(chunk_index, int) or chunk_index < 0:
        raise ValueError("chunk_index must be a non-negative integer.")

    embedding = validate_embedding(chunk.get("embedding"))
    token_count = int(chunk.get("token_count", 0))

    # Match the database validator before sending the write.
    if token_count < 50 or token_count > 1200:
        raise ValueError(
            f"token_count must be between 50 and 1200; received {token_count}."
        )

    now = _utc_now()

    return {
        "article_id": _to_object_id(article_id),
        "article_title": article_title.strip(),
        "article_status": article_status,
        "article_slug": article_slug.strip(),
        "category": category.strip(),
        "sub_category": sub_category.strip() if sub_category else "",
        "article_updated_at": article_updated_at or now,
        "chunk_index": chunk_index,
        "heading_path": (chunk.get("heading_path", "") or "").strip(),
        "content": content,
        "token_count": token_count,
        "embedding": embedding,
        "embedding_model": MODEL_NAME,
        "embedding_dim": EMBEDDING_DIM,
        "content_hash": chunk.get("content_hash", "") or "",
        "updated_at": now,
    }


def upsert_chunks(
    *,
    article_id,
    article_title: str,
    article_status: str,
    category: str,
    chunks: Sequence[Dict],
    sub_category: str = "",
    article_slug: str = "",
    article_updated_at=None,
    replace_existing: bool = True,
    session=None,
) -> Dict:
    """Upsert article chunks; optionally participate in a Mongo transaction."""
    article_object_id = _to_object_id(article_id)

    prepared_documents = [
        prepare_chunk_document(
            article_id=article_object_id,
            article_title=article_title,
            article_status=article_status,
            category=category,
            sub_category=sub_category,
            article_slug=article_slug,
            article_updated_at=article_updated_at,
            chunk=chunk,
        )
        for chunk in chunks
    ]

    if not prepared_documents:
        deleted = 0
        if replace_existing:
            delete_result = article_chunks_collection.delete_many(
                {"article_id": article_object_id},
                session=session,
            )
            deleted = delete_result.deleted_count

        return {
            "article_id": str(article_object_id),
            "upserted": 0,
            "modified": 0,
            "deleted": deleted,
            "total": 0,
        }

    operations = []
    for document in prepared_documents:
        operations.append(
            UpdateOne(
                {
                    "article_id": article_object_id,
                    "chunk_index": document["chunk_index"],
                },
                {
                    "$set": document,
                    "$setOnInsert": {
                        "created_at": _utc_now()
                    },
                },
                upsert=True,
            )
        )

    result = article_chunks_collection.bulk_write(
        operations,
        ordered=True,
        session=session,
    )

    deleted = 0
    if replace_existing:
        valid_indexes = [
            document["chunk_index"] for document in prepared_documents
        ]
        delete_result = article_chunks_collection.delete_many(
            {
                "article_id": article_object_id,
                "chunk_index": {"$nin": valid_indexes},
            },
            session=session,
        )
        deleted = delete_result.deleted_count

    return {
        "article_id": str(article_object_id),
        "upserted": result.upserted_count,
        "modified": result.modified_count,
        "deleted": deleted,
        "total": len(prepared_documents),
    }


def delete_article_chunks(*, article_id, session=None) -> int:
    article_object_id = _to_object_id(article_id)
    result = article_chunks_collection.delete_many(
        {"article_id": article_object_id},
        session=session,
    )
    return result.deleted_count


def get_article_chunks(*, article_id) -> List[Dict]:
    article_object_id = _to_object_id(article_id)
    return list(
        article_chunks_collection.find(
            {"article_id": article_object_id}
        ).sort("chunk_index", 1)
    )


def count_article_chunks(*, article_id) -> int:
    article_object_id = _to_object_id(article_id)
    return article_chunks_collection.count_documents(
        {"article_id": article_object_id}
    )


def verify_chunk_embeddings(*, article_id=None, expected_dim=EMBEDDING_DIM) -> Dict:
    query = {}
    if article_id is not None:
        query["article_id"] = _to_object_id(article_id)

    documents = list(
        article_chunks_collection.find(
            query,
            {
                "_id": 1,
                "article_id": 1,
                "chunk_index": 1,
                "embedding": 1,
            },
        )
    )

    invalid = []
    for document in documents:
        try:
            validate_embedding(
                document.get("embedding"),
                expected_dim=expected_dim,
            )
        except ValueError as exc:
            invalid.append(
                {
                    "chunk_id": str(document["_id"]),
                    "article_id": str(document["article_id"]),
                    "chunk_index": document.get("chunk_index"),
                    "reason": str(exc),
                }
            )

    return {
        "checked": len(documents),
        "valid": len(documents) - len(invalid),
        "invalid": len(invalid),
        "errors": invalid,
        "expected_dimension": expected_dim,
    }