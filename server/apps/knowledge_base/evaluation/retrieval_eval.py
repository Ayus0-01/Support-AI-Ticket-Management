from __future__ import annotations

import json
from pathlib import Path

from apps.knowledge_base.ticket_retrieval import (
    retrieve_for_ticket,
)

from .loader import (
    load_retrieval_cases,
)
from .metrics import (
    recall_at_k,
    reciprocal_rank,
    summarize_retrieval,
)


def _run_case(
    case,
):
    ticket = case.ticket.to_ticket_dict()

    retrieval = retrieve_for_ticket(
        ticket=ticket,
        include_internal=False,
        limit=30,
        top_k=5,
        rerank_candidates=20,
        context_budget=4000,
    )

    results = retrieval[
        "results"
    ]

    retrieved_ids = [
        str(
            result["article_id"]
        )
        for result in results
        if result.get(
            "article_id"
        ) is not None
    ]

    rerank_scores = [
        result.get(
            "rerank_score"
        )
        for result in results
        if result.get(
            "rerank_score"
        ) is not None
    ]

    return {
        "id": case.case_id,
        "evaluation_ticket_id": (
            case.ticket.evaluation_ticket_id
        ),
        "queries": retrieval[
            "queries"
        ],
        "retrieved_article_ids": (
            retrieved_ids
        ),
        "expected_article_ids": list(
            case.expected_article_ids
        ),
        "recall_at_1": recall_at_k(
            retrieved_ids,
            case.expected_article_ids,
            1,
        ),
        "recall_at_5": recall_at_k(
            retrieved_ids,
            case.expected_article_ids,
            5,
        ),
        "rrf_or_rank_score": (
            reciprocal_rank(
                retrieved_ids,
                case.expected_article_ids,
            )
        ),
        "rerank_score": (
            float(
                rerank_scores[0]
            )
            if rerank_scores
            else None
        ),
    }


def run(
    golden_path: str | Path,
    output_path: str | Path | None = None,
):
    cases = load_retrieval_cases(
        golden_path
    )

    case_results = [
        _run_case(case)
        for case in cases
    ]

    report = {
        "dataset": str(
            golden_path
        ),
        "summary": summarize_retrieval(
            case_results
        ),
        "cases": case_results,
    }

    if output_path:
        Path(
            output_path
        ).write_text(
            json.dumps(
                report,
                indent=2,
            ),
            encoding="utf-8",
        )

    return report


def main():
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--golden",
        default=(
            "evaluation_data/"
            "retrieval_golden.json"
        ),
    )

    parser.add_argument(
        "--output",
        default=(
            "evaluation_data/"
            "retrieval_report.json"
        ),
    )

    args = parser.parse_args()

    report = run(
        golden_path=args.golden,
        output_path=args.output,
    )

    print(
        json.dumps(
            report["summary"],
            indent=2,
        )
    )


if __name__ == "__main__":
    main()