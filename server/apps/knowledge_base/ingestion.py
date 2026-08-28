from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from bson import ObjectId

from AIticket.db import (
    knowledge_articles_collection,
)

from .loaders import load_document
from .persistence import (
    create_ingestion_job,
    update_ingestion_job,
)
from .services import (
    create_knowledge_article,
    publish_knowledge_article,
)


SUPPORTED_EXTENSIONS = {
    ".md",
    ".markdown",
    ".html",
    ".htm",
    ".docx",
    ".pdf",
}


def _utc_now():
    return datetime.now(
        timezone.utc
    )


def start_ingestion_job(
    *,
    job_type="BULK_UPLOAD",
    source_ref="",
    triggered_by_id=None,
):
    """
    Create and start an ingestion job.
    """
    job = create_ingestion_job(
        job_type=job_type,
        source_ref=source_ref,
        triggered_by_id=triggered_by_id,
    )

    started_at = _utc_now()

    update_ingestion_job(
        job_id=job["_id"],
        status="RUNNING",
        started_at=started_at,
    )

    job["status"] = "RUNNING"
    job["started_at"] = started_at

    return job


def finish_ingestion_job(
    *,
    job_id,
    progress,
    errors,
    started_at,
):
    """
    Finish an ingestion job with a deterministic final status.
    """
    finished_at = _utc_now()

    duration_ms = int(
        (
            finished_at
            - started_at
        ).total_seconds()
        * 1000
    )

    failed = progress.get(
        "failed",
        0,
    )

    final_status = (
        "COMPLETED_WITH_ERRORS"
        if failed > 0
        else "COMPLETED"
    )

    update_ingestion_job(
        job_id=job_id,
        status=final_status,
        progress=progress,
        errors=errors,
        finished_at=finished_at,
        duration_ms=duration_ms,
    )

    return {
        "job_id": job_id,
        "status": final_status,
        "progress": progress,
        "errors": errors,
        "finished_at": finished_at,
        "duration_ms": duration_ms,
    }


def _validate_document_path(
    path,
):
    """
    Validate a supported source document.
    """
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Document does not exist: {file_path}"
        )

    if not file_path.is_file():
        raise ValueError(
            f"Not a file: {file_path}"
        )

    if (
        file_path.suffix.lower()
        not in SUPPORTED_EXTENSIONS
    ):
        raise ValueError(
            "Unsupported document type: "
            f"{file_path.suffix}"
        )

    return file_path


def _make_article_slug(
    title,
    path,
):
    """
    Generate a deterministic local-ingestion slug.

    Existing slug collisions are handled by the update path.
    """
    import re

    base = (
        title
        or Path(path).stem
        or "knowledge-article"
    ).strip().lower()

    base = re.sub(
        r"[^a-z0-9]+",
        "-",
        base,
    ).strip("-")

    return base or "knowledge-article"


def _extract_category(
    metadata,
    default="General",
):
    """
    Read category metadata when supplied.

    The loader itself does not invent classification.
    """
    category = (
        metadata.get(
            "category"
        )
        if metadata
        else None
    )

    return (
        str(category).strip()
        if category
        else default
    )


def _extract_sub_category(
    metadata,
    default="General",
):
    sub_category = (
        metadata.get(
            "sub_category"
        )
        if metadata
        else None
    )

    return (
        str(sub_category).strip()
        if sub_category
        else default
    )


def _find_existing_article(
    *,
    slug,
):
    return knowledge_articles_collection.find_one(
        {
            "slug": slug
        }
    )


def _create_or_update_article(
    *,
    loaded_document: Dict,
    source_metadata: Optional[Dict],
    triggered_by_id=None,
    triggered_by_name="Ingestion",
):
    """
    Create a new DRAFT article or update an existing article.

    The actual indexing/publishing is delegated to the canonical
    publish_knowledge_article() workflow.
    """
    source_metadata = (
        source_metadata
        or {}
    )

    title = (
        loaded_document.get(
            "title",
            "",
        )
        or "Untitled Article"
    ).strip()

    content = (
        loaded_document.get(
            "text",
            "",
        )
        or ""
    ).strip()

    if not content:
        raise ValueError(
            "Loaded document contains no searchable text."
        )

    slug = _make_article_slug(
        title,
        loaded_document.get(
            "source_path"
        ),
    )

    category = _extract_category(
        source_metadata
    )

    sub_category = _extract_sub_category(
        source_metadata
    )

    existing = _find_existing_article(
        slug=slug
    )

    now = _utc_now()

    if existing:
        """
        Update the authored article.

        Version is incremented because the content represented by
        this source document is a new authored version.
        """
        next_version = (
            int(
                existing.get(
                    "version",
                    1,
                )
            )
            + 1
        )

        update = {
            "title": title,
            "category": category,
            "sub_category": sub_category,
            "content": content,
            "tags": source_metadata.get(
                "tags",
                existing.get(
                    "tags",
                    [],
                ),
            ),
            "source_system": source_metadata.get(
                "source_system",
                existing.get(
                    "source_system",
                    "UPLOAD",
                ),
            ),
            "source_url": loaded_document.get(
                "source_url"
            ),
            "source_updated_at": loaded_document.get(
                "source_updated_at"
            ),
            "updated_at": now,
            "version": next_version,
            "index_error": None,
        }

        result = (
            knowledge_articles_collection.update_one(
                {
                    "_id": existing["_id"]
                },
                {
                    "$set": update
                },
            )
        )

        if (
            result.matched_count
            != 1
        ):
            raise RuntimeError(
                "Failed to update existing knowledge article."
            )

        article = (
            knowledge_articles_collection.find_one(
                {
                    "_id": existing["_id"]
                }
            )
        )

        return article, False

    if triggered_by_id is None:
        author_id = ObjectId()
    else:
        author_id = triggered_by_id

    article = create_knowledge_article(
        title=title,
        slug=slug,
        category=category,
        sub_category=sub_category,
        tags=source_metadata.get(
            "tags",
            [],
        ),
        content=content,
        author_id=author_id,
        author_name=triggered_by_name,
        source_system=source_metadata.get(
            "source_system",
            "UPLOAD",
        ),
        source_url=loaded_document.get(
            "source_url"
        ),
        source_updated_at=loaded_document.get(
            "source_updated_at"
        ),
        visible_to_departments=source_metadata.get(
            "visible_to_departments",
            [],
        ),
        is_internal_only=source_metadata.get(
            "is_internal_only",
            False,
        ),
    )

    return article, True


def process_document(
    *,
    path,
    source_metadata=None,
    triggered_by_id=None,
    triggered_by_name="Ingestion",
):
    """
    Process one document through the canonical M2 path:

        Load
          ↓
        Normalize
          ↓
        Chunk
          ↓
        Batch Embed
          ↓
        Publish/index
          ↓
        Verify

    Returns a per-document result.
    """
    file_path = _validate_document_path(
        path
    )

    loaded = load_document(
        file_path
    )

    if not loaded.get(
        "text",
        "",
    ).strip():
        raise ValueError(
            "Document loader returned empty text."
        )

    article, created = (
        _create_or_update_article(
            loaded_document=loaded,
            source_metadata=source_metadata,
            triggered_by_id=triggered_by_id,
            triggered_by_name=triggered_by_name,
        )
    )

    published = publish_knowledge_article(
        article_id=article["_id"],
        changed_by_id=(
            article.get(
                "author_id"
            )
            or triggered_by_id
        ),
        changed_by_name=(
            article.get(
                "author_name"
            )
            or triggered_by_name
        ),
        change_note=(
            "Bulk ingestion: "
            + file_path.name
        ),
    )

    chunk_count = int(
        published.get(
            "chunk_count",
            0,
        )
    )

    indexed_version = (
        published.get(
            "indexed_version"
        )
    )

    if indexed_version != published.get(
        "version"
    ):
        raise RuntimeError(
            "Article publish completed without a matching indexed_version."
        )

    if chunk_count <= 0:
        raise RuntimeError(
            "Article publish completed without indexed chunks."
        )

    return {
        "path": str(
            file_path
        ),
        "article_id": str(
            published["_id"]
        ),
        "title": published.get(
            "title"
        ),
        "version": published.get(
            "version"
        ),
        "indexed_version": indexed_version,
        "chunk_count": chunk_count,
        "created": created,
        "status": published.get(
            "status"
        ),
        "embedding_model": published.get(
            "embedding_model"
        ),
        "source_url": loaded.get(
            "source_url"
        ),
    }


def ingest_documents(
    *,
    paths: Iterable,
    job_type="BULK_UPLOAD",
    source_ref="",
    triggered_by_id=None,
    triggered_by_name="Ingestion",
    source_metadata=None,
):
    """
    Execute a real M2 bulk-ingestion job.

    Each document is isolated operationally:
        - success increments processed
        - failure increments failed and records an error

    One bad document does not stop the remaining documents.
    """
    normalized_paths = list(
        paths
    )

    job = start_ingestion_job(
        job_type=job_type,
        source_ref=source_ref,
        triggered_by_id=triggered_by_id,
    )

    started_at = job[
        "started_at"
    ]

    progress = {
        "total_documents": len(
            normalized_paths
        ),
        "processed": 0,
        "articles_created": 0,
        "articles_updated": 0,
        "failed": 0,
        "chunks_created": 0,
        "chunks_embedded": 0,
    }

    errors: List[Dict] = []
    results: List[Dict] = []

    # Persist the total immediately so a status page sees it
    # even while the first document is processing.
    update_ingestion_job(
        job_id=job["_id"],
        progress=progress,
        errors=errors,
    )

    for index, path in enumerate(
        normalized_paths,
        start=1,
    ):
        try:
            result = process_document(
                path=path,
                source_metadata=source_metadata,
                triggered_by_id=triggered_by_id,
                triggered_by_name=triggered_by_name,
            )

            results.append(
                result
            )

            progress["processed"] += 1

            if result["created"]:
                progress[
                    "articles_created"
                ] += 1
            else:
                progress[
                    "articles_updated"
                ] += 1

            progress[
                "chunks_created"
            ] += result[
                "chunk_count"
            ]

            progress[
                "chunks_embedded"
            ] += result[
                "chunk_count"
            ]

        except Exception as exc:
            progress["failed"] += 1

            errors.append(
                {
                    "document": str(
                        path
                    ),
                    "stage": _infer_failure_stage(
                        exc
                    ),
                    "message": str(
                        exc
                    ),
                }
            )

        update_ingestion_job(
            job_id=job["_id"],
            status="RUNNING",
            progress=progress,
            errors=errors,
        )

    completion = finish_ingestion_job(
        job_id=job["_id"],
        progress=progress,
        errors=errors,
        started_at=started_at,
    )

    completion[
        "results"
    ] = results

    return completion


def _infer_failure_stage(
    exc: Exception,
) -> str:
    """
    Convert common ingestion failures into stable,
    user-facing pipeline stages.
    """
    module = (
        exc.__class__.__module__
        or ""
    ).lower()

    message = str(
        exc
    ).lower()

    if (
        "unsupported document"
        in message
        or "document does not exist"
        in message
        or "not a file"
        in message
    ):
        return "LOAD"

    if (
        "normalize"
        in message
        or "normal"
        in message
    ):
        return "NORMALIZE"

    if (
        "chunk"
        in message
    ):
        return "CHUNK"

    if (
        "embed"
        in message
        or "embedding"
        in message
    ):
        return "EMBED"

    if (
        "mongo"
        in module
        or "pymongo"
        in module
        or "article_chunks"
        in message
    ):
        return "PERSIST"

    return "PUBLISH"