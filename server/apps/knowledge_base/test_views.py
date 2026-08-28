from unittest.mock import patch

from bson import ObjectId
from django.test import SimpleTestCase
from django.urls import resolve
from rest_framework.test import APIRequestFactory

from apps.knowledge_base import services, views


class KnowledgeBaseViewTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_article_detail_route_supports_get(self):
        match = resolve(f"/api/knowledge/articles/{ObjectId()}/")

        self.assertEqual(match.func, views.update_knowledge_article_view)
        self.assertIn("get", match.func.cls.http_method_names)

    def test_non_admin_cannot_read_a_draft_article(self):
        request = self.factory.get(f"/api/knowledge/articles/{ObjectId()}/")
        draft = {
            "_id": ObjectId(),
            "status": "DRAFT",
            "is_internal_only": False,
        }

        with patch.object(
            views,
            "_get_authenticated_kb_user",
            return_value=({"role": "User"}, None),
        ), patch.object(
            views,
            "get_knowledge_article",
            return_value=draft,
        ):
            response = views.update_knowledge_article_view(
                request,
                article_id=str(draft["_id"]),
            )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["message"], "Knowledge article not found.")

    def test_public_article_list_excludes_internal_only_metadata(self):
        with patch.object(
            services.knowledge_articles_collection,
            "find",
        ) as find_articles:
            find_articles.return_value.sort.return_value = []

            articles = services.get_knowledge_articles(role="User")

        self.assertEqual(articles, [])
        find_articles.assert_called_once_with(
            {
                "status": "PUBLISHED",
                "is_internal_only": {"$ne": True},
            }
        )

    def test_upload_endpoint_rejects_missing_files(self):
        request = self.factory.post("/api/knowledge/ingest-upload/", {})

        with patch.object(
            views,
            "_get_authenticated_admin",
            return_value=({"_id": str(ObjectId()), "username": "admin"}, None),
        ):
            response = views.ingest_uploaded_documents_view(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["message"], "At least one document file is required.")

    def test_upload_endpoint_returns_original_file_names_not_staging_paths(self):
        upload = self.factory.post(
            "/api/knowledge/ingest-upload/",
            {
                "files": [
                    self._uploaded_document(),
                ],
                "source_metadata": "{}",
            },
            format="multipart",
        )

        def ingestion_result(*, paths, **_kwargs):
            return {
                "job_id": ObjectId(),
                "status": "COMPLETED_WITH_ERRORS",
                "progress": {"total_documents": 1},
                "results": [{"path": paths[0], "title": "VPN Guide"}],
                "errors": [{"document": paths[0], "message": "sample warning"}],
            }

        with patch.object(
            views,
            "_get_authenticated_admin",
            return_value=({"_id": str(ObjectId()), "username": "admin"}, None),
        ), patch.object(
            views,
            "ingest_documents",
            side_effect=ingestion_result,
        ):
            response = views.ingest_uploaded_documents_view(upload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["path"], "vpn-guide.md")
        self.assertEqual(response.data["errors"][0]["document"], "vpn-guide.md")
        self.assertEqual(len(response.data["job_id"]), 24)

    @staticmethod
    def _uploaded_document():
        from django.core.files.uploadedfile import SimpleUploadedFile

        return SimpleUploadedFile(
            "vpn-guide.md",
            b"# VPN Guide\n\nUse the approved VPN client.",
            content_type="text/markdown",
        )
