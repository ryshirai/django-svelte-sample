import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from application.errors.authentication import (
    AuthenticationInvalidCredentialsError,
    RegistrationEmailAlreadyUsedError,
)
from application.services.registration import (
    CreateRegistrationInput,
    create_registration,
)
from application.services.session import CreateSessionInput, create_session


@pytest.mark.django_db
def test_create_registration_stores_normalized_email() -> None:
    user = create_registration(
        input=CreateRegistrationInput(email="  A@Example.COM ", password="password1")
    )
    assert user.username == "a@example.com"
    assert user.email == "a@example.com"


@pytest.mark.django_db
def test_create_registration_rejects_duplicate_email() -> None:
    payload = CreateRegistrationInput(email="a@example.com", password="password1")
    create_registration(input=payload)
    with pytest.raises(RegistrationEmailAlreadyUsedError):
        create_registration(input=payload)


@pytest.mark.django_db
def test_create_session_rejects_invalid_password() -> None:
    create_registration(
        input=CreateRegistrationInput(email="a@example.com", password="password1")
    )
    with pytest.raises(AuthenticationInvalidCredentialsError):
        create_session(
            input=CreateSessionInput(email="a@example.com", password="wrongpass")
        )


@pytest.mark.django_db
def test_registration_api_starts_session() -> None:
    client = APIClient()
    response = client.post(
        "/api/v1/registrations",
        {"email": "a@example.com", "password": "password1"},
        format="json",
    )
    assert response.status_code == 201
    assert response.json()["email"] == "a@example.com"
    me = client.get("/api/v1/current-user")
    assert me.status_code == 200
    assert me.json()["email"] == "a@example.com"


@pytest.mark.django_db
def test_session_api_logs_in_and_out() -> None:
    User.objects.create_user(
        username="a@example.com",
        email="a@example.com",
        password="password1",
    )
    client = APIClient()
    login_response = client.post(
        "/api/v1/sessions",
        {"email": "a@example.com", "password": "password1"},
        format="json",
    )
    assert login_response.status_code == 200
    assert client.get("/api/v1/current-user").status_code == 200
    logout_response = client.delete("/api/v1/sessions")
    assert logout_response.status_code == 204
    assert client.get("/api/v1/current-user").status_code == 401
    assert client.get("/api/v1/current-user").json()["error"]["code"] == (
        "authentication.required"
    )


@pytest.mark.django_db
def test_current_user_requires_authentication() -> None:
    client = APIClient()
    response = client.get("/api/v1/current-user")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "authentication.required"
