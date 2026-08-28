from django.urls import path

from .views import (
    create_knowledge_article_view,
    list_knowledge_articles_view,
    update_knowledge_article_view,
    publish_knowledge_article_view,
    preview_knowledge_article_view,
    search_knowledge_base_view,
    ingest_documents_view,
    ingest_uploaded_documents_view,
    ingestion_status_view,
    knowledge_gaps_view,
)

urlpatterns = [
    path("articles/", list_knowledge_articles_view, name="knowledge-articles"),
    path("articles/create/", create_knowledge_article_view, name="knowledge-article-create-legacy"),
    path("articles/<str:article_id>/", update_knowledge_article_view, name="knowledge-article-update"),
    path("articles/<str:article_id>/publish/", publish_knowledge_article_view, name="knowledge-article-publish"),
    path("articles/<str:article_id>/preview-chunks/", preview_knowledge_article_view, name="knowledge-article-preview-chunks"),
    path("search/", search_knowledge_base_view, name="knowledge-search"),
    path("ingest/", ingest_documents_view, name="knowledge-ingest"),
    path("ingest-upload/", ingest_uploaded_documents_view, name="knowledge-ingest-upload"),
    path("ingest/<str:job_id>/", ingestion_status_view, name="knowledge-ingest-status"),
    path("gaps/", knowledge_gaps_view, name="knowledge-gaps"),
]
