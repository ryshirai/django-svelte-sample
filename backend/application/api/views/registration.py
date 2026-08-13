from django.contrib.auth import login
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from application.api.serializers.authentication import (
    CreateRegistrationInputSerializer,
    CurrentUserOutputSerializer,
)
from application.services.registration import (
    CreateRegistrationInput,
    create_registration,
)


@api_view(["POST"])
@permission_classes([AllowAny])
def registration_create(request: Request) -> Response:
    serializer = CreateRegistrationInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = create_registration(
        input=CreateRegistrationInput(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
    )
    # 登録成功でそのまま session を張る。
    login(request, user)
    output = CurrentUserOutputSerializer(
        {
            "id": user.id,
            "email": user.email,
            "is_staff": user.is_staff,
        }
    )
    return Response(output.data, status=status.HTTP_201_CREATED)
