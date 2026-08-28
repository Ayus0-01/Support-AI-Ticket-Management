from unittest.mock import patch

from apps.knowledge_base.reranker import rerank_results


results = [
    {
        "article_id": "1",
        "article_title": "Result A",
        "content": "Content A",
        "rrf_score": 0.05,
    },
    {
        "article_id": "2",
        "article_title": "Result B",
        "content": "Content B",
        "rrf_score": 0.04,
    },
]


with patch(
    "apps.knowledge_base.reranker._score_pair",
    side_effect=RuntimeError("test failure"),
):
    output = rerank_results(
        query="test query",
        results=results,
        top_k=5,
    )


print("FALLBACK RESULTS:")
for result in output:
    print(result)