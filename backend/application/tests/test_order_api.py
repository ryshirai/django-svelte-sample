import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from application.models.order import Order
from application.tests.part_fixtures import create_compatible_parts


def _login(*, email: str, is_staff: bool = False) -> APIClient:
    User.objects.create_user(
        username=email,
        email=email,
        password="password1",
        is_staff=is_staff,
    )
    client = APIClient()
    response = client.post(
        "/api/v1/sessions",
        {"email": email, "password": "password1"},
        format="json",
    )
    assert response.status_code == 200
    return client


@pytest.mark.django_db
def test_order_create_then_get_matches() -> None:
    parts = create_compatible_parts()
    client = _login(email="buyer@example.com")
    payload = {
        "part_ids": [
            parts["cpu"].id,
            parts["motherboard"].id,
            parts["memory"].id,
            parts["storage"].id,
            parts["psu"].id,
            parts["case"].id,
        ],
        "recipient_name": "山田太郎",
        "postal_code": "1600022",
        "prefecture": "東京都",
        "city": "新宿区",
        "address_line": "新宿1-1-1",
        "phone": "09012345678",
    }
    created = client.post("/api/v1/orders", payload, format="json")
    assert created.status_code == 201
    public_id = created.json()["public_id"]
    detail = client.get(f"/api/v1/orders/{public_id}")
    assert detail.status_code == 200
    body = detail.json()
    assert body["public_id"] == public_id
    assert body["status"] == "paid"
    assert len(body["lines"]) == 6


@pytest.mark.django_db
def test_order_create_rejects_duplicate_part_id() -> None:
    parts = create_compatible_parts()
    client = _login(email="buyer@example.com")
    response = client.post(
        "/api/v1/orders",
        {
            "part_ids": [
                parts["cpu"].id,
                parts["cpu"].id,
                parts["motherboard"].id,
                parts["memory"].id,
                parts["storage"].id,
                parts["psu"].id,
                parts["case"].id,
            ],
            "recipient_name": "山田太郎",
            "postal_code": "1600022",
            "prefecture": "東京都",
            "city": "新宿区",
            "address_line": "新宿1-1-1",
            "phone": "09012345678",
        },
        format="json",
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "configuration.duplicate_category"
    assert Order.objects.count() == 0


@pytest.mark.django_db
def test_order_show_hides_other_users_order() -> None:
    parts = create_compatible_parts()
    owner = _login(email="owner@example.com")
    created = owner.post(
        "/api/v1/orders",
        {
            "part_ids": [
                parts["cpu"].id,
                parts["motherboard"].id,
                parts["memory"].id,
                parts["storage"].id,
                parts["psu"].id,
                parts["case"].id,
            ],
            "recipient_name": "山田太郎",
            "postal_code": "1600022",
            "prefecture": "東京都",
            "city": "新宿区",
            "address_line": "新宿1-1-1",
            "phone": "09012345678",
        },
        format="json",
    )
    public_id = created.json()["public_id"]
    other = _login(email="other@example.com")
    response = other.get(f"/api/v1/orders/{public_id}")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "order.not_found"


@pytest.mark.django_db
def test_staff_parts_forbidden_for_customer() -> None:
    client = _login(email="buyer@example.com")
    response = client.get("/api/v1/staff/parts")
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "authentication.staff_required"


@pytest.mark.django_db
def test_parts_require_authentication() -> None:
    client = APIClient()
    response = client.get("/api/v1/parts")
    assert response.status_code == 401


@pytest.mark.django_db
def test_staff_can_cancel_order() -> None:
    parts = create_compatible_parts()
    buyer = _login(email="buyer@example.com")
    created = buyer.post(
        "/api/v1/orders",
        {
            "part_ids": [
                parts["cpu"].id,
                parts["motherboard"].id,
                parts["memory"].id,
                parts["storage"].id,
                parts["psu"].id,
                parts["case"].id,
            ],
            "recipient_name": "山田太郎",
            "postal_code": "1600022",
            "prefecture": "東京都",
            "city": "新宿区",
            "address_line": "新宿1-1-1",
            "phone": "09012345678",
        },
        format="json",
    )
    public_id = created.json()["public_id"]
    staff = _login(email="staff@example.com", is_staff=True)
    cancel = staff.post(f"/api/v1/staff/orders/{public_id}/cancel")
    assert cancel.status_code == 204
    assert Order.objects.get(public_id=public_id).status == Order.Status.CANCELLED
