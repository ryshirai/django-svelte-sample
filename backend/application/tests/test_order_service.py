from uuid import uuid4

import pytest
from django.contrib.auth.models import User

from application.errors.configuration import ConfigurationSocketMismatchError
from application.errors.order import (
    OrderInsufficientStockError,
    OrderInvalidStatusTransitionError,
    OrderNotFoundError,
    OrderPartUnlistedError,
)
from application.errors.part import PartNotFoundError
from application.models.order import Order
from application.selectors.order import get_order_for_user
from application.services.order import (
    CreateOrderInput,
    OrderPublicIdInput,
    cancel_order,
    create_order,
    prepare_order,
    ship_order,
)
from application.services.part import create_part
from application.tests.part_fixtures import (
    compatible_part_ids,
    create_compatible_parts,
    part_input,
)


def _user() -> User:
    return User.objects.create_user(
        username="buyer@example.com",
        email="buyer@example.com",
        password="buyerpass",
    )


def _order_input(*, user_id: int, part_ids: list[int]) -> CreateOrderInput:
    return CreateOrderInput(
        user_id=user_id,
        part_ids=tuple(part_ids),
        recipient_name="山田太郎",
        postal_code="1600022",
        prefecture="東京都",
        city="新宿区",
        address_line="新宿1-1-1",
        phone="09012345678",
    )


@pytest.mark.django_db
def test_create_order_persists_snapshot_and_decrements_stock() -> None:
    user = _user()
    parts = create_compatible_parts()
    part_ids = [
        parts["cpu"].id,
        parts["motherboard"].id,
        parts["memory"].id,
        parts["storage"].id,
        parts["psu"].id,
        parts["case"].id,
    ]
    public_id = create_order(input=_order_input(user_id=user.id, part_ids=part_ids))
    order = Order.objects.get(public_id=public_id)
    assert order.status == Order.Status.PAID
    assert order.lines.count() == 6
    expected_total = (
        parts["cpu"].unit_price
        + parts["motherboard"].unit_price
        + parts["memory"].unit_price
        + parts["storage"].unit_price
        + parts["psu"].unit_price
        + parts["case"].unit_price
    )
    assert order.total_price == expected_total
    parts["cpu"].refresh_from_db()
    assert parts["cpu"].stock_quantity == 9


@pytest.mark.django_db
def test_create_order_rejects_incompatible_socket() -> None:
    user = _user()
    parts = create_compatible_parts()
    bad_cpu = create_part(
        input=part_input(
            sku="CPU-1700",
            name="Intel",
            category="cpu",
            socket="lga1700",
            tdp_watts=65,
        )
    )
    part_ids = [
        bad_cpu,
        parts["motherboard"].id,
        parts["memory"].id,
        parts["storage"].id,
        parts["psu"].id,
        parts["case"].id,
    ]
    with pytest.raises(ConfigurationSocketMismatchError):
        create_order(input=_order_input(user_id=user.id, part_ids=part_ids))
    assert Order.objects.count() == 0


@pytest.mark.django_db
def test_create_order_rejects_unlisted_part() -> None:
    user = _user()
    parts = create_compatible_parts()
    parts["cpu"].is_listed = False
    parts["cpu"].save(update_fields=["is_listed"])
    with pytest.raises(OrderPartUnlistedError):
        create_order(
            input=_order_input(
                user_id=user.id,
                part_ids=[
                    parts["cpu"].id,
                    parts["motherboard"].id,
                    parts["memory"].id,
                    parts["storage"].id,
                    parts["psu"].id,
                    parts["case"].id,
                ],
            )
        )


@pytest.mark.django_db
def test_create_order_rejects_insufficient_stock() -> None:
    user = _user()
    parts = create_compatible_parts()
    parts["cpu"].stock_quantity = 0
    parts["cpu"].save(update_fields=["stock_quantity"])
    with pytest.raises(OrderInsufficientStockError):
        create_order(
            input=_order_input(
                user_id=user.id,
                part_ids=[
                    parts["cpu"].id,
                    parts["motherboard"].id,
                    parts["memory"].id,
                    parts["storage"].id,
                    parts["psu"].id,
                    parts["case"].id,
                ],
            )
        )


@pytest.mark.django_db
def test_create_order_rejects_unknown_part() -> None:
    user = _user()
    with pytest.raises(PartNotFoundError):
        create_order(input=_order_input(user_id=user.id, part_ids=[999_999]))


@pytest.mark.django_db
def test_cancel_order_restores_stock() -> None:
    user = _user()
    parts = create_compatible_parts()
    public_id = create_order(
        input=_order_input(
            user_id=user.id,
            part_ids=[
                parts["cpu"].id,
                parts["motherboard"].id,
                parts["memory"].id,
                parts["storage"].id,
                parts["psu"].id,
                parts["case"].id,
            ],
        )
    )
    cancel_order(input=OrderPublicIdInput(public_id=public_id))
    parts["cpu"].refresh_from_db()
    assert parts["cpu"].stock_quantity == 10
    assert Order.objects.get(public_id=public_id).status == Order.Status.CANCELLED


@pytest.mark.django_db
def test_cancel_order_rejects_shipped() -> None:
    user = _user()
    public_id = create_order(
        input=_order_input(user_id=user.id, part_ids=compatible_part_ids())
    )
    prepare_order(input=OrderPublicIdInput(public_id=public_id))
    ship_order(input=OrderPublicIdInput(public_id=public_id))
    with pytest.raises(OrderInvalidStatusTransitionError):
        cancel_order(input=OrderPublicIdInput(public_id=public_id))


@pytest.mark.django_db
def test_prepare_order_rejects_cancelled() -> None:
    user = _user()
    public_id = create_order(
        input=_order_input(user_id=user.id, part_ids=compatible_part_ids())
    )
    cancel_order(input=OrderPublicIdInput(public_id=public_id))
    with pytest.raises(OrderInvalidStatusTransitionError):
        prepare_order(input=OrderPublicIdInput(public_id=public_id))


@pytest.mark.django_db
def test_get_order_for_user_hides_other_users_order() -> None:
    owner = _user()
    other = User.objects.create_user(
        username="other@example.com",
        email="other@example.com",
        password="buyerpass",
    )
    public_id = create_order(
        input=_order_input(user_id=owner.id, part_ids=compatible_part_ids())
    )
    with pytest.raises(OrderNotFoundError):
        get_order_for_user(public_id=public_id, user_id=other.id)
    with pytest.raises(OrderNotFoundError):
        get_order_for_user(public_id=uuid4(), user_id=owner.id)
