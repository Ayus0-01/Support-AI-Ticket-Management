from datetime import datetime, timezone

from bson import ObjectId

from AIticket.db import (
    ticket_responses_collection,
    response_citations_collection,
    resolution_feedback_collection,
    kb_gaps_collection,
    retrieval_logs_collection,
    tickets_collection,
    ingestion_jobs_collection,
)


def _to_object_id(value):
    if isinstance(value, ObjectId):
        return value

    return ObjectId(str(value))


def create_retrieval_log(
    *,
    ticket_id,
    queries_used,
    chunks_retrieved,
    results,
):
    now = datetime.now(timezone.utc)

    document = {
        "ticket_id": _to_object_id(ticket_id),
        "queries_used": queries_used,
        "chunks_retrieved": chunks_retrieved,
        "results": [
            {
                "article_id": result.get(
                    "article_id"
                ),
                "article_title": result.get(
                    "article_title"
                ),
                "chunk_index": result.get(
                    "chunk_index"
                ),
                "rerank_score": result.get(
                    "rerank_score"
                ),
                "retrieval_rank": index,
            }
            for index, result in enumerate(
                results,
                start=1,
            )
        ],
        "created_at": now,
    }

    result = retrieval_logs_collection.insert_one(
        document
    )

    document["_id"] = result.inserted_id

    return document


def create_ticket_response(
    *,
    ticket,
    resolution,
    retrieval_log,
    queries_used,
    model="qwen3:4b",
    prompt_version="resolution.v1",
    embedding_model="BAAI/bge-large-en-v1.5",
    tokens_in=None,
    tokens_out=None,
    latency_ms=None,
):
    now = datetime.now(timezone.utc)

    response = {
        "ticket_id": _to_object_id(
            ticket["_id"]
        ),
        "ticket_number": ticket.get(
            "ticket_id"
        ),

        "sufficient_context": resolution.get(
            "sufficient_context",
            False,
        ),

        "summary": resolution.get(
            "summary",
            "",
        ),

        "steps": resolution.get(
            "steps",
            [],
        ),

        "sources": resolution.get(
            "sources",
            [],
        ),

        "escalation_recommended": resolution.get(
            "escalation_recommended",
            False,
        ),

        "escalation_reason": resolution.get(
            "escalation_reason"
        ),

        "steps_generated": resolution.get(
            "steps_generated",
            len(
                resolution.get(
                    "steps",
                    [],
                )
            ),
        ),

        "steps_dropped": resolution.get(
            "steps_dropped",
            0,
        ),

        "dropped_details": resolution.get(
            "dropped_details",
            [],
        ),

        "confidence": resolution.get(
            "confidence",
            0.0,
        ),

        "confidence_parts": resolution.get(
            "confidence_parts",
            {},
        ),

        "retrieval_log_id": retrieval_log[
            "_id"
        ],

        "queries_used": queries_used,

        "chunks_retrieved": len(
            retrieval_log.get(
                "results",
                [],
            )
        ),

        "model": model,
        "prompt_version": prompt_version,
        "embedding_model": embedding_model,

        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "latency_ms": latency_ms,

        "status": "DRAFT",

        "reviewed_by_id": None,
        "reviewed_at": None,
        "edit_diff": None,
        "reject_reason": None,

        "created_at": now,
    }

    result = ticket_responses_collection.insert_one(
        response
    )

    response["_id"] = result.inserted_id

    return response


def create_response_citations(
    *,
    response,
    retrieval_results=None,
):
    """
    Persist flattened citation records using the
    actual retrieved chunk metadata.
    """

    retrieval_results = (
        retrieval_results or []
    )

    retrieval_map = {}

    for rank, result in enumerate(
        retrieval_results,
        start=1,
    ):
        article_id = result.get(
            "article_id"
        )

        chunk_index = result.get(
            "chunk_index"
        )

        if article_id is None or chunk_index is None:
            continue

        key = (
            str(article_id),
            int(chunk_index),
        )

        retrieval_map[key] = {
            "article_id": article_id,
            "article_title": result.get(
                "article_title"
            ),
            "heading_path": result.get(
                "heading_path",
                "",
            ),
            "snippet": (
                result.get(
                    "content",
                    "",
                )[:500]
            ),
            "rerank_score": result.get(
                "rerank_score"
            ),
            "retrieval_rank": rank,
        }

    documents = []

    for step in (
        response.get(
            "steps",
            [],
        )
    ):
        step_order = step.get(
            "order"
        )

        for source in (
            step.get(
                "sources",
                []
            )
        ):
            normalized = (
                source
                .replace(
                    "[SOURCE:",
                    "",
                )
                .replace(
                    "]",
                    "",
                )
            )

            try:
                article_id, chunk_index = (
                    normalized.rsplit(
                        "#",
                        1,
                    )
                )

                chunk_index = int(
                    chunk_index
                )

            except ValueError:
                continue

            metadata = retrieval_map.get(
                (
                    article_id,
                    chunk_index,
                )
            )

            # A source that passed the citation guardrail
            # should have corresponding retrieval metadata.
            if metadata is None:
                continue

            documents.append(
                {
                    "response_id": response[
                        "_id"
                    ],
                    "ticket_id": response[
                        "ticket_id"
                    ],
                    "step_order": step_order,
                    "article_id": (
                        metadata[
                            "article_id"
                        ]
                    ),
                    "article_title": (
                        metadata[
                            "article_title"
                        ]
                    ),
                    "chunk_index": chunk_index,
                    "heading_path": (
                        metadata[
                            "heading_path"
                        ]
                    ),
                    "snippet": (
                        metadata[
                            "snippet"
                        ]
                    ),
                    "rerank_score": (
                        metadata[
                            "rerank_score"
                        ]
                    ),
                    "retrieval_rank": (
                        metadata[
                            "retrieval_rank"
                        ]
                    ),
                    "created_at": datetime.now(
                        timezone.utc
                    ),
                }
            )

    if not documents:
        return []

    result = (
        response_citations_collection.insert_many(
            documents
        )
    )

    for document, inserted_id in zip(
        documents,
        result.inserted_ids,
    ):
        document["_id"] = inserted_id

    return documents


def record_kb_gap(
    *,
    ticket_id,
    reason,
):
    now = datetime.now(
        timezone.utc
    )

    result = kb_gaps_collection.update_one(
        {
            "ticket_id": _to_object_id(
                ticket_id
            ),
            "status": "OPEN",
        },
        {
            "$set": {
                "last_reason": reason,
                "updated_at": now,
            },
            "$inc": {
                "occurrence_count": 1,
            },
            "$setOnInsert": {
                "ticket_id": _to_object_id(
                    ticket_id
                ),
                "status": "OPEN",
                "first_seen_at": now,
            },
        },
        upsert=True,
    )

    return result


def create_resolution_feedback(
    *,
    response_id,
    ticket_id,
    user_id,
    was_helpful,
    comment="",
    resolved_ticket=False,
):
    document = {
        "response_id": _to_object_id(
            response_id
        ),
        "ticket_id": _to_object_id(
            ticket_id
        ),
        "user_id": _to_object_id(
            user_id
        ),
        "was_helpful": was_helpful,
        "comment": comment,
        "resolved_ticket": resolved_ticket,
        "created_at": datetime.now(
            timezone.utc
        ),
    }

    result = resolution_feedback_collection.insert_one(
        document
    )

    document["_id"] = result.inserted_id

    return document

def mark_ticket_resolution_generated(
    *,
    ticket_id,
    response_id,
):
    from AIticket.db import tickets_collection

    tickets_collection.update_one(
        {
            "_id": _to_object_id(
                ticket_id
            )
        },
        {
            "$set": {
                "has_resolution": True,
                "resolution_status": "DRAFT",
                "latest_response_id": _to_object_id(
                    response_id
                ),
            }
        },
    )

def get_ticket_responses(
    *,
    ticket_id,
):
    responses = list(
        ticket_responses_collection.find(
            {
                "ticket_id": _to_object_id(
                    ticket_id
                )
            }
        ).sort(
            "created_at",
            -1,
        )
    )

    return responses


def get_ticket_response(
    *,
    response_id,
):
    return ticket_responses_collection.find_one(
        {
            "_id": _to_object_id(
                response_id
            )
        }
    )


def update_ticket_response_status(
    *,
    response_id,
    status,
    reviewed_by_id=None,
    reviewed_at=None,
    reject_reason=None,
    edit_diff=None,
):
    update = {
        "status": status,
    }

    if reviewed_by_id is not None:
        update["reviewed_by_id"] = _to_object_id(
            reviewed_by_id
        )

    if reviewed_at is not None:
        update["reviewed_at"] = reviewed_at

    if reject_reason is not None:
        update["reject_reason"] = reject_reason

    if edit_diff is not None:
        update["edit_diff"] = edit_diff

    result = ticket_responses_collection.update_one(
        {
            "_id": _to_object_id(
                response_id
            )
        },
        {
            "$set": update
        },
    )

    return result

def update_ticket_resolution_state(
    *,
    ticket_id,
    resolution_status,
    response_id=None,
):
    update = {
        "resolution_status": resolution_status,
    }

    if response_id is not None:
        update["latest_response_id"] = _to_object_id(
            response_id
        )

    tickets_collection.update_one(
        {
            "_id": _to_object_id(
                ticket_id
            )
        },
        {
            "$set": update
        },
    )

def create_ingestion_job(
    *,
    job_type,
    source_ref="",
    triggered_by_id=None,
):
    now = datetime.now(
        timezone.utc
    )

    document = {
        "job_type": job_type,
        "source_ref": source_ref,
        "triggered_by_id": (
            _to_object_id(triggered_by_id)
            if triggered_by_id
            else None
        ),
        "status": "QUEUED",
        "progress": {
            "total_documents": 0,
            "processed": 0,
            "articles_created": 0,
            "articles_updated": 0,
            "failed": 0,
            "chunks_created": 0,
            "chunks_embedded": 0,
        },
        "errors": [],
        "started_at": None,
        "finished_at": None,
        "duration_ms": None,
        "created_at": now,
    }

    result = ingestion_jobs_collection.insert_one(
        document
    )

    document["_id"] = result.inserted_id
    return document


def update_ingestion_job(
    *,
    job_id,
    status=None,
    progress=None,
    errors=None,
    started_at=None,
    finished_at=None,
    duration_ms=None,
):
    update = {}

    if status is not None:
        update["status"] = status

    if progress is not None:
        update["progress"] = progress

    if errors is not None:
        update["errors"] = errors

    if started_at is not None:
        update["started_at"] = started_at

    if finished_at is not None:
        update["finished_at"] = finished_at

    if duration_ms is not None:
        update["duration_ms"] = duration_ms

    if not update:
        return None

    result = ingestion_jobs_collection.update_one(
        {
            "_id": _to_object_id(job_id)
        },
        {
            "$set": update
        },
    )

    return result

def get_ingestion_job(
    *,
    job_id,
):
    """
    Fetch one ingestion job for the M2 status endpoint.
    """
    return ingestion_jobs_collection.find_one(
        {
            "_id": _to_object_id(
                job_id
            )
        }
    )


def get_kb_gaps(
    *,
    status="OPEN",
    limit=50,
):
    """
    Return Knowledge Base gaps ordered by occurrence.
    """
    if limit <= 0:
        raise ValueError(
            "limit must be greater than zero."
        )

    query = {}

    if status:
        query["status"] = status

    return list(
        kb_gaps_collection.find(
            query
        )
        .sort(
            [
                ("occurrence_count", -1),
                ("updated_at", -1),
            ]
        )
        .limit(limit)
    )