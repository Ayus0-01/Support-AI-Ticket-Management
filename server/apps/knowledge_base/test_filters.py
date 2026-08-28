from unittest.mock import patch

from apps.knowledge_base.filters import apply_retrieval_filters


ARTICLE_ID = "000000000000000000000001"


def make_result():
    return {
        "article_id": ARTICLE_ID,
        "article_title": "Test Article",
        "category": "VPN",
        "article_status": "PUBLISHED",
        "content": "Test content",
        "rrf_score": 0.05,
    }


def make_article(
    *,
    status="PUBLISHED",
    category="VPN",
    visible_to_departments=None,
    is_internal_only=False,
):
    from bson import ObjectId

    return {
        "_id": ObjectId(ARTICLE_ID),
        "category": category,
        "status": status,
        "visible_to_departments": (
            visible_to_departments or []
        ),
        "is_internal_only": is_internal_only,
    }


def run_test(
    name,
    article,
    expected_count,
    **filter_kwargs,
):
    with patch(
        "apps.knowledge_base.filters.knowledge_articles_collection.find"
    ) as mock_find:

        mock_find.return_value = [article]

        results = apply_retrieval_filters(
            [make_result()],
            **filter_kwargs,
        )

        passed = len(results) == expected_count

        print(
            f"{name}: "
            f"{'PASS' if passed else 'FAIL'} "
            f"(expected={expected_count}, "
            f"actual={len(results)})"
        )


if __name__ == "__main__":
    run_test(
        "Open to all departments",
        make_article(),
        1,
        department="Finance",
    )

    run_test(
        "Allowed department",
        make_article(
            visible_to_departments=[
                "Finance",
                "HR",
            ]
        ),
        1,
        department="Finance",
    )

    run_test(
        "Blocked department",
        make_article(
            visible_to_departments=[
                "Finance",
                "HR",
            ]
        ),
        0,
        department="Engineering",
    )

    run_test(
        "Internal article blocked",
        make_article(
            is_internal_only=True,
        ),
        0,
        department="Finance",
        include_internal=False,
    )

    run_test(
        "Internal article allowed",
        make_article(
            is_internal_only=True,
        ),
        1,
        department="Finance",
        include_internal=True,
    )

    run_test(
        "Archived article blocked",
        make_article(
            status="ARCHIVED",
        ),
        0,
        department="Finance",
    )