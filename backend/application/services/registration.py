from dataclasses import dataclass

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from django.db.models import Q

from application.errors.authentication import RegistrationEmailAlreadyUsedError
from application.errors.input import InputInvalidError
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
    if User.objects.filter(Q(username=email) | Q(email=email)).exists():
        raise RegistrationEmailAlreadyUsedError()
    _ensure_password_policy(password=input.password, email=email)
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
    # シード用。既存なら作らず、staff でなければ昇格する。
    email = normalize_email(email=input.email)
    existing = User.objects.filter(Q(username=email) | Q(email=email)).first()
    if existing is not None:
        if not existing.is_staff:
            existing.is_staff = True
            existing.save(update_fields=["is_staff"])
        return None
    user = User.objects.create_user(
        username=email,
        email=email,
        password=input.password,
    )
    user.is_staff = True
    user.save(update_fields=["is_staff"])
    return user


def _ensure_password_policy(*, password: str, email: str) -> None:
    # 公開登録だけ Django 既定バリデータを通す。シードパスワードは仕様固定。
    candidate = User(username=email, email=email)
    try:
        validate_password(password, user=candidate)
    except DjangoValidationError as error:
        raise InputInvalidError(details={"password": list(error.messages)}) from error
