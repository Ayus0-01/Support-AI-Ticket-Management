from datetime import datetime, timezone
from bson import ObjectId
from AIticket.db import (
    knowledge_articles_collection,
    article_versions_collection,
    article_chunks_collection,
)
from .retrieval import hybrid_search

def to_object_id(value):
    if isinstance(value, ObjectId):
        return value

    return ObjectId(str(value))

def create_knowledge_article(
    *,
    title,
    slug,
    category,
    sub_category,
    tags,
    content,
    author_id,
    author_name,
    source_system="MANUAL",
    source_url=None,
    source_updated_at=None,
    visible_to_departments=None,
    is_internal_only=False,
):
    existing_article = knowledge_articles_collection.find_one(
    {"slug": slug}
    )

    if existing_article:
        raise ValueError(
            "An article with this slug already exists."
        )
    now = datetime.now(timezone.utc)

    article = {
        "slug": slug,
        "title": title,
        "category": category,
        "sub_category": sub_category,
        "tags": tags or [],
        "content": content,
        "content_hash": None,
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

def get_knowledge_articles(
    *,
    role,
    include_archived=False,
):
    query = {}
    if role == "Admin":
        if include_archived:
            query["status"] = {
                "$in": [
                    "DRAFT",
                    "PUBLISHED",
                    "ARCHIVED",
                ]
            }
        else:
            query["status"] = {
                "$in": [
                    "DRAFT",
                    "PUBLISHED",
                ]
            }
    else:
        query["status"] = "PUBLISHED"
    articles = list(
        knowledge_articles_collection.find(
            query
        ).sort(
            "updated_at",
            -1
        )
    )

    return articles

def create_article_version(
    *,
    article,
    changed_by_id,
    changed_by_name,
    change_note,
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
        version_document
    )
    version_document["_id"] = result.inserted_id
    return version_document

def create_article_chunks(
    *,
    article,
    chunk_size=500,
):
    content = article["content"].strip()

    if not content:
        raise ValueError(
            "Article content cannot be empty."
        )

    words = content.split()

    chunks = []

    for start in range(0, len(words), chunk_size):
        chunk_words = words[
            start:start + chunk_size
        ]

        chunk_content = " ".join(
            chunk_words
        ).strip()

        if not chunk_content:
            continue

        chunk = {
            "article_id": article["_id"],
            "chunk_index": len(chunks),
            "article_title": article["title"],
            "article_status": article["status"],
            "article_slug": article["slug"],
            "category": article["category"],
            "article_updated_at": article["updated_at"],
            "heading_path": "",
            "content": chunk_content,
            "token_count": len(chunk_words),
            "embedding": None,
            "embedding_model": None,
            "embedding_dim": None,
            "created_at": datetime.now(timezone.utc),
        }

        chunks.append(chunk)

    return chunks

def save_article_chunks(chunks):
    if not chunks:
        return []

    result = article_chunks_collection.insert_many(
        chunks
    )

    for chunk, inserted_id in zip(
        chunks,
        result.inserted_ids
    ):
        chunk["_id"] = inserted_id

    return chunks

def update_article_chunk_count(
    *,
    article_id,
    chunk_count,
):
    knowledge_articles_collection.update_one(
        {"_id": to_object_id(article_id)},
        {
            "$set": {
                "chunk_count": chunk_count,
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )

def rebuild_article_chunks(*, article):
    article_id = article["_id"]

    article_chunks_collection.delete_many(
        {
            "article_id": article_id
        }
    )

    chunks = create_article_chunks(
        article=article
    )

    saved_chunks = save_article_chunks(
        chunks
    )

    update_article_chunk_count(
        article_id=article_id,
        chunk_count=len(saved_chunks),
    )

    return saved_chunks

def embed_article_chunks(*, article):
    chunks = list(
        article_chunks_collection.find(
            {
                "article_id": article["_id"]
            }
        ).sort(
            "chunk_index",
            1
        )
    )

    if not chunks:
        return []

    from .embeddings import generate_embedding

    updated_chunks = []

    for chunk in chunks:
        embedding = generate_embedding(
            chunk["content"]
        )

        if len(embedding) != 1024:
            raise ValueError(
                "Embedding dimension must be 1024."
            )

        article_chunks_collection.update_one(
            {
                "_id": chunk["_id"]
            },
            {
                "$set": {
                    "embedding": embedding,
                    "embedding_model": (
                        "BAAI/bge-large-en-v1.5"
                    ),
                    "embedding_dim": 1024,
                }
            }
        )

        chunk["embedding"] = embedding
        chunk["embedding_model"] = (
            "BAAI/bge-large-en-v1.5"
        )
        chunk["embedding_dim"] = 1024

        updated_chunks.append(chunk)

    return updated_chunks

def mark_article_indexed(
    *,
    article_id,
    indexed_version,
    embedding_model,
):
    knowledge_articles_collection.update_one(
        {
            "_id": to_object_id(article_id),
        },
        {
            "$set": {
                "indexed_version": indexed_version,
                "last_indexed_at": datetime.now(timezone.utc),
                "embedding_model": embedding_model,
                "index_error": None,
            }
        },
    )

def search_knowledge_base(
    *,
    query,
    status="PUBLISHED",
    limit=10,
    top_k=5,
):
    """
    Search the Knowledge Base using the complete
    retrieval pipeline:

        Vector Search
        Keyword Search
        RRF Fusion
        Local Reranking

    Returns the final reranked results.
    """

    return hybrid_search(
        query=query,
        status=status,
        limit=limit,
        top_k=top_k,
    )