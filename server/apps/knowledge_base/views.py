import json
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from bson import ObjectId
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from AIticket.db import users_collection
from .serializers import (
    CreateKnowledgeArticleSerializer,
    UpdateKnowledgeArticleSerializer,
    PublishKnowledgeArticleSerializer,
    PreviewChunksSerializer,
    KnowledgeSearchSerializer,
    KnowledgeArticleListSerializer,
    KnowledgeArticleDetailSerializer,
    ChunkPreviewSerializer,
    IngestionRequestSerializer,
)
from .services import (
    create_knowledge_article,
    get_knowledge_article,
    update_knowledge_article,
    get_knowledge_articles,
    publish_knowledge_article,
    create_article_chunks,
    search_knowledge_base,
)
from .ingestion import ingest_documents
from .persistence import get_ingestion_job, get_kb_gaps

@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def create_knowledge_article_view(request):
    """
    Create a new Knowledge Base article.

    Only Admin users are allowed to author articles.
    The author identity comes from the authenticated JWT.
    """

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return Response(
            {
                "message": "Authorization header missing."
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Extract and validate JWT

    try:
        parts = auth_header.split(" ")

        if len(parts) != 2 or parts[0] != "Bearer":
            return Response(
                {
                    "message": "Invalid Authorization header."
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        access_token = AccessToken(parts[1])
        user_id = access_token["user_id"]

    except Exception:
        return Response(
            {
                "message": "Invalid or expired token."
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Find authenticated user

    try:
        user = users_collection.find_one(
            {
                "_id": ObjectId(user_id)
            }
        )

    except Exception:
        return Response(
            {
                "message": "Invalid user ID."
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not user:
        return Response(
            {
                "message": "User not found."
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    # Admin-only authorization

    if user.get("role", "User") != "Admin":
        return Response(
            {
                "message": "Admin access required."
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    # Validate request data

    serializer = CreateKnowledgeArticleSerializer(
        data=request.data
    )

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Create article

    try:
        article = create_knowledge_article(
            **serializer.validated_data,
            author_id=user_id,
            author_name=user["username"],
        )

        article["_id"] = str(article["_id"])
        if article.get("author_id"):
            article["author_id"] = str(
                article["author_id"]
            )
        
    except ValueError as exc:
        return Response(
            {
                "message": str(exc)
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    return Response(
        {
            "message": "Knowledge Base article created successfully.",
            "article": article,
        },
        status=status.HTTP_201_CREATED,
    )

@api_view(["GET", "POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def list_knowledge_articles_view(request):
    """
    List Knowledge Base articles for GET, or create one for POST.
    """

    if request.method == "POST":
        # POST /api/knowledge/articles/ uses the same creation contract
        # as the existing compatibility endpoint.
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return Response({"message": "Authorization header missing."}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            parts = auth_header.split(" ")
            if len(parts) != 2 or parts[0] != "Bearer":
                raise ValueError
            access_token = AccessToken(parts[1])
            user_id = access_token["user_id"]
            user = users_collection.find_one({"_id": ObjectId(user_id)})
        except Exception:
            return Response({"message": "Invalid or expired token."}, status=status.HTTP_401_UNAUTHORIZED)
        if not user:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        if user.get("role", "User") != "Admin":
            return Response({"message": "Admin access required."}, status=status.HTTP_403_FORBIDDEN)
        serializer = CreateKnowledgeArticleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            article = create_knowledge_article(**serializer.validated_data, author_id=user_id, author_name=user.get("username", "Unknown"))
        except ValueError as exc:
            return Response({"message": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        article["_id"] = str(article["_id"])
        if article.get("author_id"):
            article["author_id"] = str(article["author_id"])
        return Response({"message": "Knowledge Base article created successfully.", "article": article}, status=status.HTTP_201_CREATED)

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return Response(
            {
                "message": "Authorization header missing."
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Extract and validate JWT

    try:
        parts = auth_header.split(" ")

        if len(parts) != 2 or parts[0] != "Bearer":
            return Response(
                {
                    "message": "Invalid Authorization header."
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        access_token = AccessToken(parts[1])
        user_id = access_token["user_id"]

    except Exception:
        return Response(
            {
                "message": "Invalid or expired token."
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Find authenticated user

    try:
        user = users_collection.find_one(
            {
                "_id": ObjectId(user_id)
            }
        )

    except Exception:
        return Response(
            {
                "message": "Invalid user ID."
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not user:
        return Response(
            {
                "message": "User not found."
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    role = user.get("role", "User")

    # Archived articles are visible only to Admins

    include_archived = (
        request.query_params.get("include_archived") == "true"
        and role == "Admin"
    )

    # Get articles

    articles = get_knowledge_articles(
        role=role,
        include_archived=include_archived,
    )

    # Convert MongoDB documents to API-safe JSON

    for article in articles:
        article["_id"] = str(article["_id"])

    safe_articles = KnowledgeArticleListSerializer(
        articles,
        many=True,
    ).data

    return Response(
        {
            "articles": safe_articles,
        },
        status=status.HTTP_200_OK,
    )

@api_view(["GET", "POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def search_knowledge_base_view(request):
    """
    Search the Knowledge Base using the complete
    hybrid + reranking retrieval pipeline.
    """

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return Response(
            {
                "message": "Authorization header missing."
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    try:
        parts = auth_header.split(" ")

        if len(parts) != 2 or parts[0] != "Bearer":
            return Response(
                {
                    "message": "Invalid Authorization header."
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        access_token = AccessToken(parts[1])
        user_id = access_token["user_id"]

    except Exception:
        return Response(
            {
                "message": "Invalid or expired token."
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    try:
        user = users_collection.find_one(
            {
                "_id": ObjectId(user_id)
            }
        )

    except Exception:
        return Response(
            {
                "message": "Invalid user ID."
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not user:
        return Response(
            {
                "message": "User not found."
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    role = user.get("role", "User")

    if request.method == "POST":
        serializer = KnowledgeSearchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        query = data["query"]
        limit = data["limit"]
        top_k = data["top_k"]
        category = data.get("category")
        department = data.get("department")
        include_internal = data.get("include_internal", False) and role == "Admin"
    else:
        query = request.query_params.get("q", "").strip()
        if not query:
            return Response({"message": "Search query is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            limit = int(request.query_params.get("limit", 10))
            top_k = int(request.query_params.get("top_k", 5))
        except ValueError:
            return Response({"message": "limit and top_k must be integers."}, status=status.HTTP_400_BAD_REQUEST)
        category = request.query_params.get("category")
        department = request.query_params.get("department")
        include_internal = (request.query_params.get("include_internal", "false") == "true" and role == "Admin")

    try:
        results = search_knowledge_base(
            query=query,
            status="PUBLISHED",
            limit=limit,
            top_k=top_k,
            category=category,
            department=department,
            include_internal=include_internal,
        )

    except ValueError as exc:
        return Response(
            {
                "message": str(exc)
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    safe_results = []

    for result in results:

        safe_result = dict(result)

        if safe_result.get("article_id"):
            safe_result["article_id"] = str(
                safe_result["article_id"]
            )

        safe_results.append(
            safe_result
        )

    return Response(
        {
            "query": query,
            "results": safe_results,
        },
        status=status.HTTP_200_OK,
    )

@api_view(["GET", "PUT"])
@authentication_classes([])
@permission_classes([AllowAny])
def update_knowledge_article_view(request, article_id):
    if request.method == "GET":
        user, error = _get_authenticated_kb_user(request)
        if error:
            return error

        try:
            article = get_knowledge_article(article_id=article_id)
        except ValueError as exc:
            return Response(
                {"message": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
            user.get("role", "User") != "Admin"
            and (
                article.get("status") != "PUBLISHED"
                or article.get("is_internal_only", False)
            )
        ):
            return Response(
                {"message": "Knowledge article not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        article["_id"] = str(article["_id"])
        for key in ("author_id", "reviewed_by_id"):
            if article.get(key):
                article[key] = str(article[key])

        return Response(
            {"article": KnowledgeArticleDetailSerializer(article).data},
            status=status.HTTP_200_OK,
        )

    user, error = _get_authenticated_admin(request)
    if error:
        return error
    serializer = UpdateKnowledgeArticleSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    data = dict(serializer.validated_data)
    change_note = data.pop("change_note", "Article updated") or "Article updated"
    try:
        article = update_knowledge_article(
            article_id=article_id,
            updates=data,
            changed_by_id=user["_id"],
            changed_by_name=user.get("username", "Unknown"),
            change_note=change_note,
        )
    except ValueError as exc:
        return Response({"message": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    article["_id"] = str(article["_id"])
    for key in ("author_id", "reviewed_by_id"):
        if article.get(key):
            article[key] = str(article[key])
    return Response({"message": "Knowledge Base article updated successfully.", "article": KnowledgeArticleDetailSerializer(article).data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def publish_knowledge_article_view(request, article_id):
    user, error = _get_authenticated_admin(request)
    if error:
        return error
    serializer = PublishKnowledgeArticleSerializer(data=request.data or {})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    try:
        article = publish_knowledge_article(
            article_id=article_id,
            changed_by_id=user["_id"],
            changed_by_name=user.get("username", "Unknown"),
            change_note=serializer.validated_data.get("change_note", "Published"),
        )
    except ValueError as exc:
        return Response({"message": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    article["_id"] = str(article["_id"])
    for key in ("author_id", "reviewed_by_id"):
        if article.get(key):
            article[key] = str(article[key])
    return Response({"message": "Knowledge Base article published and indexed successfully.", "article": KnowledgeArticleDetailSerializer(article).data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def preview_knowledge_article_view(request, article_id):
    user, error = _get_authenticated_admin(request)
    if error:
        return error
    try:
        if request.data.get("content"):
            serializer = PreviewChunksSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            article = {
                "_id": ObjectId(article_id),
                "title": serializer.validated_data.get("title", "Preview"),
                "content": serializer.validated_data["content"],
            }
        else:
            article = get_knowledge_article(article_id=article_id)
        chunks = create_article_chunks(article=article)
    except Exception as exc:
        return Response({"message": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    preview = [
        {
            "index": chunk.get("chunk_index", 0),
            "heading_path": chunk.get("heading_path", ""),
            "token_count": chunk.get("token_count", 0),
            "content": chunk.get("content", ""),
        }
        for chunk in chunks
    ]
    return Response({"article_id": str(article_id), "chunks": ChunkPreviewSerializer(preview, many=True).data}, status=status.HTTP_200_OK)


def _get_authenticated_admin(request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None, Response({"message": "Authorization header missing."}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        parts = auth_header.split(" ")
        if len(parts) != 2 or parts[0] != "Bearer":
            raise ValueError
        token = AccessToken(parts[1])
        user_id = token["user_id"]
        user = users_collection.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None, Response({"message": "Invalid or expired token."}, status=status.HTTP_401_UNAUTHORIZED)
    if not user:
        return None, Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    if user.get("role", "User") != "Admin":
        return None, Response({"message": "Admin access required."}, status=status.HTTP_403_FORBIDDEN)
    user["_id"] = user_id
    return user, None


def _get_authenticated_kb_user(request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None, Response({"message": "Authorization header missing."}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        parts = auth_header.split(" ")
        if len(parts) != 2 or parts[0] != "Bearer":
            raise ValueError
        token = AccessToken(parts[1])
        user_id = token["user_id"]
        user = users_collection.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None, Response({"message": "Invalid or expired token."}, status=status.HTTP_401_UNAUTHORIZED)

    if not user:
        return None, Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    user["_id"] = user_id
    return user, None


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def ingest_documents_view(request):
    user, error = _get_authenticated_admin(request)
    if error:
        return error

    serializer = IngestionRequestSerializer(
        data=request.data
    )

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    data = serializer.validated_data

    try:
        result = ingest_documents(
            paths=data["paths"],
            job_type=data["job_type"],
            source_ref=data["source_ref"],
            triggered_by_id=user["_id"],
            triggered_by_name=user.get(
                "username",
                "Unknown",
            ),
            source_metadata=data.get(
                "source_metadata",
                {},
            ),
        )

        # MongoDB ObjectId is not JSON serializable.
        # Convert the job identifier at the API boundary.
        if result.get("job_id") is not None:
            result["job_id"] = str(
                result["job_id"]
            )

        return Response(
            result,
            status=status.HTTP_200_OK,
        )

    except (
        ValueError,
        FileNotFoundError,
    ) as exc:
        return Response(
            {
                "message": str(exc)
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def ingest_uploaded_documents_view(request):
    """
    Ingest files received from the authenticated Admin KB workflow.

    This is a narrow HTTP adapter around the existing ingestion service:
    uploaded files are staged only for the synchronous ingestion run, then
    discarded. The original server-path endpoint remains available for
    administrative jobs and automation.
    """
    user, error = _get_authenticated_admin(request)
    if error:
        return error

    uploads = request.FILES.getlist("files")
    if not uploads:
        return Response(
            {"message": "At least one document file is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if len(uploads) > 50:
        return Response(
            {"message": "A maximum of 50 documents can be uploaded at once."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    raw_metadata = request.data.get("source_metadata", "{}")
    try:
        source_metadata = json.loads(raw_metadata)
    except (TypeError, json.JSONDecodeError):
        return Response(
            {"message": "source_metadata must be valid JSON."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not isinstance(source_metadata, dict):
        return Response(
            {"message": "source_metadata must be a JSON object."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    max_file_size = 10 * 1024 * 1024

    try:
        with TemporaryDirectory(prefix="m2-kb-upload-") as temporary_directory:
            paths = []
            upload_names = {}

            for upload in uploads:
                original_name = Path(upload.name or "document").name
                extension = Path(original_name).suffix.lower()

                if extension not in {
                    ".md",
                    ".markdown",
                    ".html",
                    ".htm",
                    ".docx",
                    ".pdf",
                }:
                    raise ValueError(
                        f"Unsupported document type: {extension or 'unknown'}"
                    )

                if upload.size and upload.size > max_file_size:
                    raise ValueError(
                        f"Document exceeds the 10 MB limit: {original_name}"
                    )

                staged_path = (
                    Path(temporary_directory)
                    / f"{uuid4().hex}-{original_name}"
                )

                with staged_path.open("wb") as destination:
                    for chunk in upload.chunks():
                        destination.write(chunk)

                staged_path_text = str(staged_path)
                paths.append(staged_path_text)
                upload_names[staged_path_text] = original_name

            result = ingest_documents(
                paths=paths,
                job_type=request.data.get("job_type", "BULK_UPLOAD"),
                source_ref=request.data.get("source_ref", ""),
                triggered_by_id=user["_id"],
                triggered_by_name=user.get("username", "Unknown"),
                source_metadata=source_metadata,
            )

            # The staging directory is deliberately short-lived. Keep the
            # client-facing report useful without exposing stale local paths.
            for document_result in result.get("results", []):
                path = document_result.get("path")
                if path in upload_names:
                    document_result["path"] = upload_names[path]

            for document_error in result.get("errors", []):
                path = document_error.get("document")
                if path in upload_names:
                    document_error["document"] = upload_names[path]

        if result.get("job_id") is not None:
            result["job_id"] = str(result["job_id"])

        return Response(result, status=status.HTTP_200_OK)
    except (ValueError, FileNotFoundError) as exc:
        return Response(
            {"message": str(exc)},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def ingestion_status_view(request, job_id):
    user, error = _get_authenticated_admin(request)
    if error:
        return error
    try:
        job = get_ingestion_job(job_id=job_id)
    except Exception:
        return Response({"message": "Invalid ingestion job ID."}, status=status.HTTP_400_BAD_REQUEST)
    if not job:
        return Response({"message": "Ingestion job not found."}, status=status.HTTP_404_NOT_FOUND)
    job["_id"] = str(job["_id"])
    if job.get("triggered_by_id"):
        job["triggered_by_id"] = str(job["triggered_by_id"])
    return Response({"job": job}, status=status.HTTP_200_OK)


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def knowledge_gaps_view(request):
    user, error = _get_authenticated_admin(request)
    if error:
        return error
    gap_status = request.query_params.get("status", "OPEN")
    try:
        limit = int(request.query_params.get("limit", 50))
    except ValueError:
        return Response({"message": "limit must be an integer."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        gaps = get_kb_gaps(status=gap_status, limit=limit)
    except ValueError as exc:
        return Response({"message": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    safe = []
    for gap in gaps:
        item = dict(gap)
        if item.get("_id"):
            item["_id"] = str(item["_id"])
        if item.get("ticket_id"):
            item["ticket_id"] = str(item["ticket_id"])
        safe.append(item)
    return Response({"status": gap_status, "count": len(safe), "gaps": safe}, status=status.HTTP_200_OK)
