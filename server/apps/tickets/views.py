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

from AIticket.db import users_collection

from .serializers import CreateTicketSerializer
from .services import (
    create_ticket,
    get_user_tickets,
    get_ticket_by_id,
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

    return Response(
        {
            "tickets": tickets
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

    return Response(
        {
            "ticket": ticket
        },
        status=status.HTTP_200_OK
    )