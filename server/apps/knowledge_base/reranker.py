import torch

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
)


MODEL_NAME = "BAAI/bge-reranker-v2-m3"


_tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)

_model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME
)

_model.eval()


def _score_pair(
    query,
    document,
):
    """
    Compute the raw reranker score for one
    query/document pair.
    """

    inputs = _tokenizer(
        query,
        document,
        padding=True,
        truncation=True,
        return_tensors="pt",
        max_length=512,
    )

    with torch.no_grad():
        score = (
            _model(**inputs)
            .logits
            .view(-1)
            .float()
            .item()
        )

    return score


def rerank_results(
    query,
    results,
    top_k=5,
):
    """
    Rerank hybrid-search results using the
    local BGE reranker.

    Each result receives:
        rerank_score

    Results are returned in descending
    reranker score order.
    """

    if not results:
        return []

    reranked = []

    for result in results:

        content = result.get(
            "content",
            "",
        )

        title = result.get(
            "article_title",
            "",
        )

        document = (
            f"{title}\n\n"
            f"{content}"
        )

        raw_score = _score_pair(
            query,
            document,
        )

        updated_result = dict(
            result
        )

        updated_result[
            "rerank_score"
        ] = raw_score

        reranked.append(
            updated_result
        )

    reranked.sort(
        key=lambda item: item[
            "rerank_score"
        ],
        reverse=True,
    )

    return reranked[:top_k]