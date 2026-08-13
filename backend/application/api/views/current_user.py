from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from application.api.serializers.authentication import CurrentUserOutputSerializer
from application.api.views.auth_user import authenticated_user


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user_show(request: Request) -> Response:
    user = authenticated_user(request=request)
    output = CurrentUserOutputSerializer(
        {
            "id": user.id,
            "email": user.email,
            "is_staff": user.is_staff,
        }
    )
    return Response(output.data)
