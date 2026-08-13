from django.contrib.auth.models import User
from rest_framework.request import Request

from application.errors.authentication import AuthenticationRequiredError


def authenticated_user(*, request: Request) -> User:
    user = request.user
    if not user.is_authenticated or not isinstance(user, User):
        raise AuthenticationRequiredError()
    return user


def authenticated_user_id(*, request: Request) -> int:
    return authenticated_user(request=request).id
