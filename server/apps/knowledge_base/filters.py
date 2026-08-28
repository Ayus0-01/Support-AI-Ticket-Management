from AIticket.db import knowledge_articles_collection


def apply_retrieval_filters(
    results,
    *,
    category=None,
    department=None,
    include_internal=False,
):
    """
    Apply M2 Knowledge Base access filters
    after RRF fusion and before reranking.

    Rules:
    - Category must match when provided.
    - Archived articles are excluded.
    - Internal-only articles are excluded unless
      include_internal is True.
    - Articles restricted to departments are visible
      only to users from an allowed department.
    """

    if not results:
        return []

    article_ids = [
        result["article_id"]
        for result in results
        if result.get("article_id")
    ]

    articles = knowledge_articles_collection.find(
        {
            "_id": {
                "$in": article_ids
            }
        },
        {
            "_id": 1,
            "category": 1,
            "status": 1,
            "visible_to_departments": 1,
            "is_internal_only": 1,
        },
    )

    article_map = {
        str(article["_id"]): article
        for article in articles
    }

    filtered_results = []

    for result in results:
        article_id = str(
            result["article_id"]
        )

        article = article_map.get(
            article_id
        )

        if not article:
            continue

        # Archived content must never be retrieved.
        if article.get("status") == "ARCHIVED":
            continue

        # Category filter.
        if (
            category
            and article.get("category") != category
        ):
            continue

        # Internal-only access.
        if (
            article.get("is_internal_only", False)
            and not include_internal
        ):
            continue

        # Department access.
        allowed_departments = article.get(
            "visible_to_departments",
            [],
        )

        if (
            allowed_departments
            and department not in allowed_departments
        ):
            continue

        filtered_results.append(
            result
        )

    return filtered_results