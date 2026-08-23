from apps.knowledge_base.retrieval import hybrid_search


query = "VPN connection timeout"

results = hybrid_search(
    query=query,
    status="DRAFT",
    limit=10,
    top_k=5,
)


print("=" * 80)
print("HYBRID + RERANKING RETRIEVAL TEST")
print("=" * 80)

print("Query:", query)
print("Results:", len(results))

for index, result in enumerate(
    results,
    start=1,
):
    print("\n" + "-" * 80)
    print(f"RESULT {index}")
    print("-" * 80)

    print(
        "Title:",
        result.get(
            "article_title"
        ),
    )

    print(
        "RRF score:",
        result.get(
            "rrf_score"
        ),
    )

    print(
        "Rerank score:",
        result.get(
            "rerank_score"
        ),
    )

    print(
        "Content:",
        result.get(
            "content"
        ),
    )