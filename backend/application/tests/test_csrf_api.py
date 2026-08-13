import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_csrf_show_sets_cookie() -> None:
    client = APIClient()
    response = client.get("/api/v1/csrf")
    assert response.status_code == 204
    assert "csrftoken" in response.cookies


def _csrf_client() -> tuple[APIClient, str]:
    client = APIClient(enforce_csrf_checks=True)
    csrf = client.get("/api/v1/csrf")
    token = csrf.cookies["csrftoken"].value
    return client, token


@pytest.mark.django_db
def test_session_create_rejects_missing_csrf() -> None:
    client = APIClient(enforce_csrf_checks=True)
    client.get("/api/v1/csrf")
    response = client.post(
        "/api/v1/sessions",
        {"email": "a@example.com", "password": "correct-staple-9"},
        format="json",
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "input.invalid"


@pytest.mark.django_db
def test_registration_create_rejects_missing_csrf() -> None:
    client = APIClient(enforce_csrf_checks=True)
    client.get("/api/v1/csrf")
    response = client.post(
        "/api/v1/registrations",
        {"email": "a@example.com", "password": "correct-staple-9"},
        format="json",
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "input.invalid"


@pytest.mark.django_db
def test_session_create_accepts_csrf_token() -> None:
    User.objects.create_user(
        username="a@example.com",
        email="a@example.com",
        password="correct-staple-9",
    )
    client, token = _csrf_client()
    response = client.post(
        "/api/v1/sessions",
        {"email": "a@example.com", "password": "correct-staple-9"},
        format="json",
        HTTP_X_CSRFTOKEN=token,
    )
    assert response.status_code == 200
    assert response.json()["email"] == "a@example.com"


@pytest.mark.django_db
def test_session_delete_accepts_csrf_token() -> None:
    User.objects.create_user(
        username="a@example.com",
        email="a@example.com",
        password="correct-staple-9",
    )
    client, token = _csrf_client()
    login = client.post(
        "/api/v1/sessions",
        {"email": "a@example.com", "password": "correct-staple-9"},
        format="json",
        HTTP_X_CSRFTOKEN=token,
    )
    assert login.status_code == 200
    token = client.cookies["csrftoken"].value
    logout = client.delete("/api/v1/sessions", HTTP_X_CSRFTOKEN=token)
    assert logout.status_code == 204
    assert client.get("/api/v1/current-user").status_code == 401


@pytest.mark.django_db
def test_csrf_post_returns_envelope() -> None:
    client = APIClient()
    response = client.post("/api/v1/csrf")
    assert response.status_code == 405
    assert response.json()["error"]["code"] == "input.invalid"
