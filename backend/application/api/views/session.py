from django.contrib.auth import login, logout
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from application.api.serializers.authentication import (
    CreateSessionInputSerializer,
    CurrentUserOutputSerializer,
)
from application.errors.authentication import AuthenticationRequiredError
from application.services.session import CreateSessionInput, create_session


@api_view(["POST", "DELETE"])
@permission_classes([AllowAny])
def session_create(request: Request) -> Response:
    # DELETE も AllowAny。未ログインは DRF 既定ではなく authentication.required を返す。
    if request.method == "DELETE":
        return session_delete(request)
    serializer = CreateSessionInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = create_session(
        input=CreateSessionInput(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
    )
    # session cookie は View が login() する。Service は認証だけ。
    login(request, user)
    output = CurrentUserOutputSerializer(
        {
            "id": user.id,
            "email": user.email,
            "is_staff": user.is_staff,
        }
    )
    return Response(output.data)


def session_delete(request: Request) -> Response:
    if not request.user.is_authenticated:
        raise AuthenticationRequiredError()
    logout(request)
    return Response(status=204)
