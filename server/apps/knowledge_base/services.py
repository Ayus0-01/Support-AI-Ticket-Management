from datetime import datetime, timezone
from typing import List

from bson import ObjectId

from AIticket.db import (
    article_chunks_collection,
    article_versions_collection,
    knowledge_articles_collection,
)

from .chunking import chunk_document
from .embeddings import MODEL_NAME, content_hash, generate_chunk_embeddings
from .normalization import normalize_document
from .retrieval import hybrid_search
from .vectorstore import count_article_chunks, upsert_chunks


def to_object_id(value):
    if isinstance(value, ObjectId):
        return value
    try:
        return ObjectId(str(value))
    except Exception as exc:
        raise ValueError(f"Invalid ObjectId: {value}") from exc


def _utc_now():
    return datetime.now(timezone.utc)


def _mongo_client():
    return knowledge_articles_collection.database.client


def create_knowledge_article(
    *, title, slug, category, sub_category, tags, content,
    author_id, author_name, source_system="MANUAL", source_url=None,
    source_updated_at=None, visible_to_departments=None,
    is_internal_only=False,
):
    existing_article = knowledge_articles_collection.find_one({"slug": slug})
    if existing_article:
        raise ValueError("An article with this slug already exists.")

    now = _utc_now()
    article_content = (content or "").strip()
    if not article_content:
        raise ValueError("Article content cannot be empty.")

    article = {
        "slug": slug,
        "title": title,
        "category": category,
        "sub_category": sub_category,
        "tags": tags or [],
        "content": article_content,
        "content_hash": content_hash(article_content),
        "status": "DRAFT",
        "version": 1,
        "source_system": source_system,
        "source_url": source_url,
        "source_updated_at": source_updated_at,
        "visible_to_departments": visible_to_departments or [],
        "is_internal_only": is_internal_only,
        "last_indexed_at": None,
        "indexed_version": None,
        "chunk_count": 0,
        "embedding_model": None,
        "index_error": None,
        "author_id": to_object_id(author_id),
        "author_name": author_name,
        "reviewed_by_id": None,
        "created_at": now,
        "updated_at": now,
    }

    result = knowledge_articles_collection.insert_one(article)
    article["_id"] = result.inserted_id
    return article

def get_knowledge_article(
    *,
    article_id,
):
    """
    Fetch one Knowledge Base article by MongoDB ObjectId.
    """
    article_id = to_object_id(
        article_id
    )

    article = knowledge_articles_collection.find_one(
        {
            "_id": article_id
        }
    )

    if not article:
        raise ValueError(
            "Knowledge article not found."
        )

    return article

def update_knowledge_article(
    *,
    article_id,
    updates,
    changed_by_id,
    changed_by_name,
    change_note="Article updated",
):
    """
    M2 article update.

    Update + immutable version creation happen in one transaction.
    A modified published article becomes DRAFT, and its old chunks
    are moved to DRAFT so stale published guidance is not retrievable.
    """
    article_id = to_object_id(article_id)

    current = knowledge_articles_collection.find_one(
        {"_id": article_id}
    )

    if not current:
        raise ValueError(
            "Knowledge article not found."
        )

    editable_fields = {
        "title",
        "slug",
        "category",
        "sub_category",
        "tags",
        "content",
        "source_system",
        "source_url",
        "visible_to_departments",
        "is_internal_only",
    }

    clean_updates = {
        key: value
        for key, value in updates.items()
        if key in editable_fields
    }

    if not clean_updates:
        raise ValueError(
            "No editable article fields were supplied."
        )

    next_article = dict(current)
    next_article.update(clean_updates)

    content = (
        next_article.get("content", "")
        or ""
    ).strip()

    if not content:
        raise ValueError(
            "Article content cannot be empty."
        )

    duplicate = knowledge_articles_collection.find_one(
        {
            "slug": next_article["slug"],
            "_id": {"$ne": article_id},
        }
    )

    if duplicate:
        raise ValueError(
            "An article with this slug already exists."
        )

    now = _utc_now()

    next_article["content"] = content
    next_article["content_hash"] = content_hash(
        content
    )
    next_article["version"] = (
        int(current.get("version", 1)) + 1
    )
    next_article["status"] = "DRAFT"
    next_article["index_error"] = None
    next_article["updated_at"] = now

    client = _mongo_client()

    with client.start_session() as session:
        with session.start_transaction():

            knowledge_articles_collection.update_one(
                {"_id": article_id},
                {
                    "$set": {
                        key: next_article[key]
                        for key in (
                            "title",
                            "slug",
                            "category",
                            "sub_category",
                            "tags",
                            "content",
                            "content_hash",
                            "version",
                            "status",
                            "source_system",
                            "source_url",
                            "visible_to_departments",
                            "is_internal_only",
                            "index_error",
                            "updated_at",
                        )
                    }
                },
                session=session,
            )

            article_chunks_collection.update_many(
                {"article_id": article_id},
                {
                    "$set": {
                        "article_status": "DRAFT",
                        "updated_at": now,
                    }
                },
                session=session,
            )

            create_article_version(
                article=next_article,
                changed_by_id=changed_by_id,
                changed_by_name=changed_by_name,
                change_note=change_note,
                session=session,
            )

    return knowledge_articles_collection.find_one(
        {"_id": article_id}
    )


def get_knowledge_articles(*, role, include_archived=False):
    query = {}
    if role == "Admin":
        query["status"] = (
            {"$in": ["DRAFT", "PUBLISHED", "ARCHIVED"]}
            if include_archived
            else {"$in": ["DRAFT", "PUBLISHED"]}
        )
    else:
        query.update(
            {
                "status": "PUBLISHED",
                "is_internal_only": {"$ne": True},
            }
        )

    return list(
        knowledge_articles_collection.find(query).sort("updated_at", -1)
    )


def create_article_version(
    *, article, changed_by_id, changed_by_name, change_note, session=None
):
    version_document = {
        "article_id": article["_id"],
        "version": article["version"],
        "title": article["title"],
        "content": article["content"],
        "change_note": change_note,
        "changed_by_id": to_object_id(changed_by_id),
        "changed_by_name": changed_by_name,
        "changed_at": article["updated_at"],
    }

    result = article_versions_collection.insert_one(
        version_document,
        session=session,
    )
    version_document["_id"] = result.inserted_id
    return version_document


def _prepare_article_for_chunking(article):
    return normalize_document(
        {
            "title": article.get("title", ""),
            "text": article.get("content", ""),
            "headings": [],
            "source_url": article.get("source_url"),
            "source_updated_at": article.get("source_updated_at"),
            "source_path": None,
        }
    )


def create_article_chunks(*, article) -> List[dict]:
    normalized = _prepare_article_for_chunking(article)
    chunks = chunk_document(normalized)
    if not chunks:
        raise ValueError(
            "Article content produced no searchable chunks."
        )
    return chunks


def embed_article_chunks(*, article, chunks=None):
    if chunks is None:
        chunks = create_article_chunks(article=article)
    if not chunks:
        return []
    return generate_chunk_embeddings(
        chunks,
        batch_size=64,
        max_retries=3,
        backoff_seconds=1.0,
    )


def update_article_chunk_count(*, article_id, chunk_count, session=None):
    knowledge_articles_collection.update_one(
        {"_id": to_object_id(article_id)},
        {"$set": {"chunk_count": chunk_count, "updated_at": _utc_now()}},
        session=session,
    )


def rebuild_article_chunks(*, article, session=None):
    chunks = create_article_chunks(article=article)
    enriched_chunks = embed_article_chunks(article=article, chunks=chunks)

    result = upsert_chunks(
        article_id=article["_id"],
        article_title=article["title"],
        article_status=article["status"],
        category=article["category"],
        sub_category=article.get("sub_category", ""),
        article_slug=article.get("slug", ""),
        article_updated_at=article.get("updated_at"),
        chunks=enriched_chunks,
        replace_existing=True,
        session=session,
    )

    update_article_chunk_count(
        article_id=article["_id"],
        chunk_count=result["total"],
        session=session,
    )

    return {"chunks": enriched_chunks, "upsert": result}


def mark_article_indexed(
    *, article_id, indexed_version, embedding_model, session=None
):
    knowledge_articles_collection.update_one(
        {"_id": to_object_id(article_id)},
        {
            "$set": {
                "indexed_version": indexed_version,
                "last_indexed_at": _utc_now(),
                "embedding_model": embedding_model,
                "index_error": None,
            }
        },
        session=session,
    )


def search_knowledge_base(
    *, query, status="PUBLISHED", limit=10, top_k=5,
    category=None, department=None, include_internal=False,
):
    return hybrid_search(
        query=query,
        status=status,
        limit=limit,
        top_k=top_k,
        category=category,
        department=department,
        include_internal=include_internal,
    )


def publish_knowledge_article(*, article_id, changed_by_id=None,
                              changed_by_name="System", change_note="Published"):
    """
    Transactional M2 publish/index workflow.

    Embeddings are generated before the transaction because model inference
    is not a MongoDB operation. All database state changes are committed or
    rolled back together.
    """
    article_id = to_object_id(article_id)

    current = knowledge_articles_collection.find_one({"_id": article_id})
    if not current:
        raise ValueError("Knowledge article not found.")

    current_hash = content_hash(current.get("content", ""))

    already_indexed = (
        current.get("status") == "PUBLISHED"
        and current.get("indexed_version") == current.get("version")
        and current.get("embedding_model") == MODEL_NAME
        and current.get("content_hash") == current_hash
        and count_article_chunks(article_id=article_id) > 0
    )

    if already_indexed:
        return current

    # Prepare and embed outside the transaction.
    working_article = dict(current)
    working_article["status"] = "PUBLISHED"
    working_article["content_hash"] = current_hash
    working_article["updated_at"] = _utc_now()

    chunks = create_article_chunks(article=working_article)
    enriched_chunks = embed_article_chunks(
        article=working_article,
        chunks=chunks,
    )

    client = _mongo_client()

    with client.start_session() as session:
        with session.start_transaction():
            # Re-read inside the transaction to avoid publishing stale state.
            article = knowledge_articles_collection.find_one(
                {"_id": article_id},
                session=session,
            )
            if not article:
                raise ValueError("Knowledge article not found.")

            now = _utc_now()
            article["status"] = "PUBLISHED"
            article["content_hash"] = current_hash
            article["updated_at"] = now

            # Record immutable version before replacing the retrieval state.
            actor_id = changed_by_id or article.get("author_id")
            actor_name = changed_by_name or article.get("author_name", "System")
            if actor_id is None:
                raise ValueError(
                    "changed_by_id is required when the article has no author_id."
                )

            create_article_version(
                article=article,
                changed_by_id=actor_id,
                changed_by_name=actor_name,
                change_note=change_note,
                session=session,
            )

            # Atomically replace old retrieval chunks with the new set.
            result = upsert_chunks(
                article_id=article["_id"],
                article_title=article["title"],
                article_status="PUBLISHED",
                category=article["category"],
                sub_category=article.get("sub_category", ""),
                article_slug=article.get("slug", ""),
                article_updated_at=now,
                chunks=enriched_chunks,
                replace_existing=True,
                session=session,
            )

            # Do not call an independent delete here: upsert_chunks already
            # removes stale chunks in the same session/transaction.
            knowledge_articles_collection.update_one(
                {"_id": article_id},
                {
                    "$set": {
                        "status": "PUBLISHED",
                        "content_hash": current_hash,
                        "chunk_count": result["total"],
                        "indexed_version": article["version"],
                        "last_indexed_at": now,
                        "embedding_model": MODEL_NAME,
                        "index_error": None,
                        "updated_at": now,
                    }
                },
                session=session,
            )

            # Commit occurs automatically when the context exits successfully.

    return knowledge_articles_collection.find_one({"_id": article_id})
