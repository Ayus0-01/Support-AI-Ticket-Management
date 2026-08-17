from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.tokens import AccessToken
from bson import ObjectId

from AIticket.db import (
    users_collection,
    tickets_collection,
)

from .serializers import (
    CreateTicketSerializer,
    CheckDuplicateSerializer,
    PreviewClassifySerializer,
    EmployeeTicketSerializer,
    ClassificationOverrideSerializer,
    StatusTransitionSerializer,
    TicketCommentSerializer,
)
from .services import (
    create_ticket,
    enqueue_classification,
    get_user_tickets,
    get_ticket_by_id,
    check_duplicate_tickets,
    get_agent_queue,
    save_classification_override,
    apply_classification_override,
    transition_ticket_status,
    add_ticket_comment,
    get_ticket_timeline,
)
from .classification.category_classifier import (
    predict_category_fast,
)

from .classification.subcategory_classifier import (
    predict_subcategory_fast,
)

@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def create_ticket_view(request):
    """
    Create a new support ticket.

    The requester is identified from the JWT.
    The frontend cannot choose the requester.
    """

     # Get Authorization header

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return Response(
            {
                "message": "Authorization header missing."
            },
            status=status.HTTP_401_UNAUTHORIZED
        )
    
      # Extract and validate jwt

    try:
        parts = auth_header.split(" ")

        if len(parts) != 2 or parts[0] != "Bearer":
            return Response(
                {
                    "message": "Invalid Authorization header."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        token = parts[1]

        access_token = AccessToken(token)

        user_id = access_token["user_id"]

    except Exception as e:
        print("JWT error:", e)

        return Response(
            {
                "message": "Invalid or expired token."
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

        # find requester in mongodb

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
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user:
        return Response(
            {
                "message": "User not found."
            },
            status=status.HTTP_404_NOT_FOUND
        )

   # validate ticket data

    serializer = CreateTicketSerializer(data=request.data)

    if not serializer.is_valid():

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

   # create ticket

    requester = {
        "user_id": user_id,
        "username": user["username"],
        "email": user["email"],
    }

    ticket = create_ticket(
        serializer.validated_data,
        requester
    )

    enqueue_classification(
        ticket["ticket_id"]
    )

    # return created ticket

    return Response(
        {
            "message": "Ticket created successfully.",
            "ticket": ticket,
        },
        status=status.HTTP_201_CREATED
    )

@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def get_tickets_view(request):

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return Response(
            {
                "message": "Authorization header missing."
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    try:
        parts = auth_header.split(" ")

        if len(parts) != 2 or parts[0] != "Bearer":
            return Response(
                {
                    "message": "Invalid Authorization header."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        token = parts[1]

        access_token = AccessToken(token)
        user_id = access_token["user_id"]

    except Exception as e:
        print("JWT error:", e)

        return Response(
            {
                "message": "Invalid or expired token."
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    tickets = get_user_tickets(user_id)

    safe_tickets = EmployeeTicketSerializer(
        tickets,
        many=True
    ).data

    return Response(
    {
        "ticket": safe_tickets
    },
    status=status.HTTP_200_OK
)


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def get_ticket_detail_view(request, ticket_id):

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return Response(
            {
                "message": "Authorization header missing."
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    try:
        parts = auth_header.split(" ")

        if len(parts) != 2 or parts[0] != "Bearer":
            return Response(
                {
                    "message": "Invalid Authorization header."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        token = parts[1]

        access_token = AccessToken(token)
        user_id = access_token["user_id"]

    except Exception as e:
        print("JWT error:", e)

        return Response(
            {
                "message": "Invalid or expired token."
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    ticket = get_ticket_by_id(ticket_id, user_id)

    if not ticket:
        return Response(
            {
                "message": "Ticket not found."
            },
            status=status.HTTP_404_NOT_FOUND
        )

    safe_ticket = EmployeeTicketSerializer(
        ticket,
    ).data

    return Response(
        {
            "ticket": safe_ticket
        },
        status=status.HTTP_200_OK
    )

@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def check_duplicates_view(request):

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return Response(
            {
                "message": "Authorization header missing."
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    try:
        parts = auth_header.split(" ")

        if len(parts) != 2 or parts[0] != "Bearer":
            return Response(
                {
                    "message": "Invalid Authorization header."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        token = parts[1]

        access_token = AccessToken(token)

        user_id = access_token["user_id"]

    except Exception as e:
        print("JWT error:", e)

        return Response(
            {
                "message": "Invalid or expired token."
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    serializer = CheckDuplicateSerializer(
        data=request.data
    )

    if not serializer.is_valid():

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    subject = serializer.validated_data["subject"]
    description = serializer.validated_data["description"]

    duplicates = check_duplicate_tickets(
        user_id=user_id,
        subject=subject,
        description=description
    )

    return Response(
        {
            "has_duplicate": len(duplicates) > 0,
            "duplicates": duplicates
        },
        status=status.HTTP_200_OK
    )

@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def preview_classify_view(request):
    """
    FAST-only live classification preview.

    This endpoint never invokes the LLM.
    """

    serializer = PreviewClassifySerializer(
        data=request.data
    )

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    subject = serializer.validated_data[
        "subject"
    ]

    description = serializer.validated_data[
        "description"
    ]

    category_result = predict_category_fast(
        subject=subject,
        description=description,
    )

    subcategory_result = predict_subcategory_fast(
        subject=subject,
        description=description,
    )

    return Response(
        {
            "category": category_result,
            "subcategory": subcategory_result,
        },
        status=status.HTTP_200_OK
    )

@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def agent_queue_view(request):
    """
    Return the active agent queue ordered by
    time remaining until SLA breach.
    """

    auth_header = request.headers.get(
        "Authorization"
    )

    if not auth_header:
        return Response(
            {
                "message":
                    "Authorization header missing."
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    try:
        parts = auth_header.split(" ")

        if (
            len(parts) != 2
            or parts[0] != "Bearer"
        ):
            return Response(
                {
                    "message":
                        "Invalid Authorization header."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        token = parts[1]

        access_token = AccessToken(
            token
        )

        user_id = access_token[
            "user_id"
        ]

    except Exception as e:

        print(
            "JWT error:",
            e
        )

        return Response(
            {
                "message":
                    "Invalid or expired token."
            },
            status=status.HTTP_401_UNAUTHORIZED
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
                "message":
                    "Invalid user ID."
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user:
        return Response(
            {
                "message":
                    "User not found."
            },
            status=status.HTTP_404_NOT_FOUND
        )

    role = user.get(
        "role",
        "User"
    )

    if role not in {
        "Agent",
        "Admin",
    }:
        return Response(
            {
                "message":
                    "Agent access required."
            },
            status=status.HTTP_403_FORBIDDEN
        )

    tickets = get_agent_queue()

    return Response(
        {
            "tickets": tickets
        },
        status=status.HTTP_200_OK
    )

@api_view(["PATCH"])
@authentication_classes([])
@permission_classes([AllowAny])
def classification_override_view(
    request,
    ticket_id,
):
    """
    Allow an agent to correct AI classification.
    """

    auth_header = request.headers.get(
        "Authorization"
    )

    if not auth_header:
        return Response(
            {
                "message":
                    "Authorization header missing."
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    try:
        parts = auth_header.split(" ")

        if (
            len(parts) != 2
            or parts[0] != "Bearer"
        ):
            return Response(
                {
                    "message":
                        "Invalid Authorization header."
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        access_token = AccessToken(
            parts[1]
        )

        user_id = access_token[
            "user_id"
        ]

    except Exception:
        return Response(
            {
                "message":
                    "Invalid or expired token."
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
                "message":
                    "Invalid user ID."
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not user:
        return Response(
            {
                "message":
                    "User not found."
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    if user.get("role") not in {
        "Agent",
        "Admin",
    }:
        return Response(
            {
                "message":
                    "Agent access required."
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = ClassificationOverrideSerializer(
        data=request.data
    )

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    corrected_category = (
        serializer.validated_data.get(
            "category"
        )
    )

    corrected_severity = (
        serializer.validated_data.get(
            "severity"
        )
    )

    if (
        corrected_category is None
        and corrected_severity is None
    ):
        return Response(
            {
                "message":
                    "At least one correction is required."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    override = save_classification_override(
        ticket_id=ticket_id,
        agent_user_id=user_id,
        corrected_category=corrected_category,
        corrected_severity=corrected_severity,
    )

    if override is None:
        return Response(
            {
                "message":
                    "Ticket not found."
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    updated_ticket = apply_classification_override(
        ticket_id=ticket_id,
        corrected_category=corrected_category,
        corrected_severity=corrected_severity,
    )

    return Response(
        {
            "message":
                "Classification override applied.",
            "override": override,
            "updated_classification": updated_ticket,
        },
    status=status.HTTP_200_OK,
    )

@api_view(["PATCH"])
@authentication_classes([])
@permission_classes([AllowAny])
def transition_ticket_status_view(
    request,
    ticket_id,
):
    """
    Change ticket status using the centralized
    transition rules.
    """

    auth_header = request.headers.get(
        "Authorization"
    )

    if not auth_header:
        return Response(
            {
                "message":
                    "Authorization header missing."
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    try:
        parts = auth_header.split(" ")

        if (
            len(parts) != 2
            or parts[0] != "Bearer"
        ):
            return Response(
                {
                    "message":
                        "Invalid Authorization header."
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        access_token = AccessToken(
            parts[1]
        )

        user_id = access_token[
            "user_id"
        ]

    except Exception:
        return Response(
            {
                "message":
                    "Invalid or expired token."
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
                "message":
                    "Invalid user ID."
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not user:
        return Response(
            {
                "message":
                    "User not found."
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    if user.get("role") not in {
        "Agent",
        "Admin",
    }:
        return Response(
            {
                "message":
                    "Agent access required."
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = StatusTransitionSerializer(
        data=request.data
    )

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    new_status = serializer.validated_data[
        "status"
    ]

    resolution_summary = (
        serializer.validated_data.get(
            "resolution_summary",
            ""
        )
    )

    result = transition_ticket_status(
        ticket_id=ticket_id,
        new_status=new_status,
        actor_user_id=user_id,
        resolution_summary=resolution_summary,
    )

    if not result["success"]:

        if result["error"] == (
            "TICKET_NOT_FOUND"
        ):
            return Response(
                {
                    "message":
                        "Ticket not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if result["error"] == (
            "INVALID_TRANSITION"
        ):
            return Response(
                {
                    "error_code":
                        "INVALID_TRANSITION",

                    "message":
                        "The requested status transition is not allowed.",

                    "current_status":
                        result["current_status"],

                    "requested_status":
                        result["requested_status"],
                },
                status=status.HTTP_409_CONFLICT,
            )

    return Response(
        {
            "message":
                "Ticket status updated.",

            "transition": result,
        },
        status=status.HTTP_200_OK,
    )

@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def add_ticket_comment_view(
    request,
    ticket_id,
):
    """
    Add a public or internal comment to a ticket.
    Agent/Admin only.
    """

    auth_header = request.headers.get(
        "Authorization"
    )

    if not auth_header:
        return Response(
            {
                "message":
                    "Authorization header missing."
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    try:
        parts = auth_header.split(" ")

        if (
            len(parts) != 2
            or parts[0] != "Bearer"
        ):
            return Response(
                {
                    "message":
                        "Invalid Authorization header."
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        access_token = AccessToken(
            parts[1]
        )

        user_id = access_token[
            "user_id"
        ]

    except Exception:
        return Response(
            {
                "message":
                    "Invalid or expired token."
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
                "message":
                    "Invalid user ID."
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not user:
        return Response(
            {
                "message":
                    "User not found."
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    if user.get("role") not in {
        "Agent",
        "Admin",
    }:
        return Response(
            {
                "message":
                    "Agent access required."
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = TicketCommentSerializer(
        data=request.data
    )

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    comment = add_ticket_comment(
        ticket_id=ticket_id,
        author_user_id=user_id,
        comment=serializer.validated_data[
            "comment"
        ],
        visibility=serializer.validated_data[
            "visibility"
        ],
    )

    if comment is None:
        return Response(
            {
                "message":
                    "Ticket not found."
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response(
        {
            "message":
                "Comment added.",
            "comment": comment,
        },
        status=status.HTTP_201_CREATED,
    )

@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def ticket_timeline_view(
    request,
    ticket_id,
):
    """
    Return the ticket timeline.

    Employees see:
        status history
        public comments

    Agents/Admins also see:
        internal comments
    """

    auth_header = request.headers.get(
        "Authorization"
    )

    if not auth_header:
        return Response(
            {
                "message":
                    "Authorization header missing."
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    try:
        parts = auth_header.split(" ")

        if (
            len(parts) != 2
            or parts[0] != "Bearer"
        ):
            return Response(
                {
                    "message":
                        "Invalid Authorization header."
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        access_token = AccessToken(
            parts[1]
        )

        user_id = access_token[
            "user_id"
        ]

    except Exception:
        return Response(
            {
                "message":
                    "Invalid or expired token."
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
                "message":
                    "Invalid user ID."
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not user:
        return Response(
            {
                "message":
                    "User not found."
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    role = user.get(
        "role",
        "User"
    )

    ticket = tickets_collection.find_one(
        {
            "ticket_id": ticket_id
        }
    )

    if not ticket:
        return Response(
            {
                "message":
                    "Ticket not found."
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    if role in {
        "Agent",
        "Admin",
    }:
        include_internal = True

    else:
        if (
            str(
                ticket.get(
                    "requester",
                    {}
                ).get(
                    "user_id"
                )
            )
            != str(user_id)
        ):
            return Response(
                {
                    "message":
                        "Ticket not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        include_internal = False

    timeline = get_ticket_timeline(
        ticket_id=ticket_id,
        include_internal=include_internal,
    )

    return Response(
        {
            "ticket_id": ticket_id,
            "timeline": timeline,
        },
        status=status.HTTP_200_OK,
    )