import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_csrf_show_sets_cookie() -> None:
    client = APIClient()
    response = client.get("/api/v1/csrf")
    assert response.status_code == 204
    assert "csrftoken" in response.cookies
