from dataclasses import dataclass

from django.contrib.auth.models import User
from django.db import IntegrityError, transaction

from application.errors.authentication import RegistrationEmailAlreadyUsedError
from application.validators.email import normalize_email


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateRegistrationInput:
    email: str
    password: str


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateStaffUserInput:
    email: str
    password: str


@transaction.atomic
def create_registration(*, input: CreateRegistrationInput) -> User:
    # Django User の識別子は username。
    # 正規化済み email を username と email の両方に入れる。
    email = normalize_email(email=input.email)
    if User.objects.filter(username=email).exists():
        raise RegistrationEmailAlreadyUsedError()
    try:
        return User.objects.create_user(
            username=email,
            email=email,
            password=input.password,
        )
    except IntegrityError as error:
        raise RegistrationEmailAlreadyUsedError() from error


@transaction.atomic
def create_staff_user(*, input: CreateStaffUserInput) -> User | None:
    # シード用。既存なら作らず None（SKU と同様に冪等）。
    email = normalize_email(email=input.email)
    if User.objects.filter(username=email).exists():
        return None
    user = User.objects.create_user(
        username=email,
        email=email,
        password=input.password,
    )
    user.is_staff = True
    user.save(update_fields=["is_staff"])
    return user
