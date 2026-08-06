from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import RegisterSerializer, LoginSerializer
from .services import register_service, login_service


@api_view(["POST"])
def register(request):

    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():

        result = register_service(serializer.validated_data)

        if result["success"]:
            return Response(
                {
                    "message": result["message"]
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "message": result["message"]
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["POST"])
def login(request):

    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():

        result = login_service(serializer.validated_data)

        if result["success"]:
            return Response(
                {
                    "message": result["message"],
                    "access": result["access"],
                    "refresh": result["refresh"]
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "message": result["message"]
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )