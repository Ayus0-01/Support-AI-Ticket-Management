from django.urls import path
from .views import (
    create_knowledge_article_view,
    list_knowledge_articles_view,
    search_knowledge_base_view
)

urlpatterns = [
    path(
        "articles/",
        create_knowledge_article_view,
        name="create-knowledge-article",
    ),
    path(
        "articles/list/",
        list_knowledge_articles_view,
        name="list-knowledge-articles",
    ),
    path(
        "search/",
        search_knowledge_base_view,
        name="search-knowledge-base",
    ),
]