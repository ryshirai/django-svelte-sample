from dataclasses import dataclass

from django.contrib.auth.models import User

from application.errors.authentication import AuthenticationInvalidCredentialsError
from application.validators.email import normalize_email


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateSessionInput:
    email: str
    password: str


def create_session(*, input: CreateSessionInput) -> User:
    email = normalize_email(email=input.email)
    try:
        # username に正規化済み email が入っている。
        user = User.objects.get(username=email)
    except User.DoesNotExist as error:
        raise AuthenticationInvalidCredentialsError() from error
    # 不存在とパスワード違いは同じ error。
    if not user.is_active or not user.check_password(input.password):
        raise AuthenticationInvalidCredentialsError()
    return user
