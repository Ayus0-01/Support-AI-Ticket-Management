from __future__ import annotations

from statistics import mean
from typing import Iterable, Sequence


def recall_at_k(
    retrieved_article_ids: Sequence[str],
    expected_article_ids: Iterable[str],
    k: int,
) -> float:
    if k <= 0:
        raise ValueError(
            "k must be greater than zero."
        )

    expected = {
        str(value)
        for value in expected_article_ids
    }

    if not expected:
        return 0.0

    retrieved = {
        str(value)
        for value in retrieved_article_ids[:k]
    }

    return (
        1.0
        if retrieved.intersection(expected)
        else 0.0
    )


def reciprocal_rank(
    retrieved_article_ids: Sequence[str],
    expected_article_ids: Iterable[str],
) -> float:
    expected = {
        str(value)
        for value in expected_article_ids
    }

    if not expected:
        return 0.0

    for rank, article_id in enumerate(
        retrieved_article_ids,
        start=1,
    ):
        if str(article_id) in expected:
            return 1.0 / rank

    return 0.0


def summarize_retrieval(
    case_results: Sequence[dict],
) -> dict:
    if not case_results:
        return {
            "cases": 0,
            "recall_at_1": 0.0,
            "recall_at_5": 0.0,
            "mrr": 0.0,
            "mean_rerank_score": None,
        }

    recall_1 = [
        float(
            item["recall_at_1"]
        )
        for item in case_results
    ]

    recall_5 = [
        float(
            item["recall_at_5"]
        )
        for item in case_results
    ]

    reciprocal_ranks = [
        float(
            item["rrf_or_rank_score"]
        )
        for item in case_results
    ]

    rerank_scores = [
        float(
            item["rerank_score"]
        )
        for item in case_results
        if item.get(
            "rerank_score"
        ) is not None
    ]

    return {
        "cases": len(case_results),
        "recall_at_1": round(
            mean(recall_1),
            4,
        ),
        "recall_at_5": round(
            mean(recall_5),
            4,
        ),
        "mrr": round(
            mean(reciprocal_ranks),
            4,
        ),
        "mean_rerank_score": (
            round(
                mean(rerank_scores),
                4,
            )
            if rerank_scores
            else None
        ),
    }