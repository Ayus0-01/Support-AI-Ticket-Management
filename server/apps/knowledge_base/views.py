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
    KnowledgeArticleListSerializer,
)
from .services import (
    create_knowledge_article,
    get_knowledge_articles,
    search_knowledge_base
)

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

@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def list_knowledge_articles_view(request):
    """
    List Knowledge Base articles.

    Admin:
        DRAFT + PUBLISHED
        ARCHIVED when explicitly requested

    Agent/User:
        PUBLISHED only
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

@api_view(["GET"])
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

    search_status = (
        request.query_params.get(
            "status",
            "PUBLISHED",
        )
        if role == "Admin"
        else "PUBLISHED"
    )

    query = request.query_params.get(
        "q",
        "",
    ).strip()

    if not query:
        return Response(
            {
                "message": "Search query is required."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        results = search_knowledge_base(
            query=query,
            status=search_status,
            limit=int(
                request.query_params.get(
                    "limit",
                    10,
                )
            ),
            top_k=int(
                request.query_params.get(
                    "top_k",
                    5,
                )
            ),
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