from AIticket.db import article_chunks_collection
from .embeddings import generate_embedding
from .reranker import rerank_results

def vector_search(
    *,
    query,
    status="PUBLISHED",
    limit=10,
):
    query_vector = generate_embedding(query)

    pipeline = [
        {
            "$vectorSearch": {
                "index": "kb_vector_index",
                "path": "embedding",
                "queryVector": query_vector,
                "numCandidates": 100,
                "limit": limit,
                "filter": {
                    "article_status": status,
                },
            }
        },
        {
            "$project": {
                "_id": 0,
                "article_id": 1,
                "article_title": 1,
                "article_slug": 1,
                "content": 1,
                "article_status": 1,
                "score": {
                    "$meta": "vectorSearchScore",
                },
            }
        },
    ]

    return list(
        article_chunks_collection.aggregate(
            pipeline
        )
    )


def keyword_search(
    *,
    query,
    status="PUBLISHED",
    limit=10,
):
    pipeline = [
        {
            "$search": {
                "index": "kb_text_index",
                "compound": {
                    "filter": [
                        {
                            "equals": {
                                "path": "article_status",
                                "value": status,
                            }
                        }
                    ],
                    "should": [
                        {
                            "text": {
                                "query": query,
                                "path": "content",
                            }
                        },
                        {
                            "text": {
                                "query": query,
                                "path": "heading_path",
                                "score": {
                                    "boost": {
                                        "value": 2
                                    }
                                },
                            }
                        },
                        {
                            "text": {
                                "query": query,
                                "path": "article_title",
                                "score": {
                                    "boost": {
                                        "value": 2
                                    }
                                },
                            }
                        },
                    ],
                },
            }
        },
        {
            "$limit": limit
        },
        {
            "$project": {
                "_id": 0,
                "article_id": 1,
                "article_title": 1,
                "article_slug": 1,
                "content": 1,
                "article_status": 1,
                "score": {
                    "$meta": "searchScore",
                },
            }
        },
    ]

    return list(
        article_chunks_collection.aggregate(
            pipeline
        )
    )

def reciprocal_rank_fusion(
    vector_results,
    keyword_results,
    k=60,
):
    scores = {}
    documents = {}

    for rank, result in enumerate(
        vector_results,
        start=1,
    ):
        article_id = str(result["article_id"])

        scores[article_id] = (
            scores.get(article_id, 0)
            + 1 / (k + rank)
        )

        documents[article_id] = result

    for rank, result in enumerate(
        keyword_results,
        start=1,
    ):
        article_id = str(result["article_id"])

        scores[article_id] = (
            scores.get(article_id, 0)
            + 1 / (k + rank)
        )

        documents[article_id] = result

    ranked_ids = sorted(
        scores,
        key=scores.get,
        reverse=True,
    )

    fused_results = []

    for article_id in ranked_ids:
        result = documents[article_id].copy()

        result["rrf_score"] = scores[
            article_id
        ]

        fused_results.append(result)

    return fused_results

def hybrid_search(
    *,
    query,
    status="PUBLISHED",
    limit=10,
    top_k=5,
):
    """
    Run vector search and keyword search,
    fuse the results using RRF, then rerank
    the fused candidates using the local BGE
    reranker.
    """

    vector_results = vector_search(
        query=query,
        status=status,
        limit=limit,
    )

    keyword_results = keyword_search(
        query=query,
        status=status,
        limit=limit,
    )

    fused_results = reciprocal_rank_fusion(
        vector_results,
        keyword_results,
    )

    reranked_results = rerank_results(
        query=query,
        results=fused_results,
        top_k=top_k,
    )

    return reranked_results