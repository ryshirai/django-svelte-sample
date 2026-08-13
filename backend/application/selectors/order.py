from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from django.db.models import QuerySet

from application.errors.order import OrderNotFoundError
from application.models.order import Order


@dataclass(frozen=True, slots=True, kw_only=True)
class OrderLineDetail:
    category: str
    sku: str
    name: str
    unit_price: Decimal
    quantity: int


@dataclass(frozen=True, slots=True, kw_only=True)
class OrderDetail:
    public_id: UUID
    status: str
    total_price: Decimal
    created_at: datetime
    recipient_name: str
    postal_code: str
    prefecture: str
    city: str
    address_line: str
    phone: str
    lines: tuple[OrderLineDetail, ...]


def get_order_for_user(*, public_id: UUID, user_id: int) -> OrderDetail:
    # 他人の注文も存在しないものとして扱う。403 にしない。
    try:
        order = Order.objects.prefetch_related("lines").get(
            public_id=public_id,
            user_id=user_id,
        )
    except Order.DoesNotExist as error:
        raise OrderNotFoundError() from error
    return _to_order_detail(order=order)


def get_order(*, public_id: UUID) -> OrderDetail:
    # スタッフ向け。所有者では絞らない。
    try:
        order = Order.objects.prefetch_related("lines").get(public_id=public_id)
    except Order.DoesNotExist as error:
        raise OrderNotFoundError() from error
    return _to_order_detail(order=order)


def list_orders_for_user(*, user_id: int) -> QuerySet[Order]:
    return Order.objects.filter(user_id=user_id).order_by("-created_at")


def list_orders() -> QuerySet[Order]:
    return Order.objects.all().order_by("-created_at")


def _to_order_detail(*, order: Order) -> OrderDetail:
    lines = tuple(
        OrderLineDetail(
            category=line.category,
            sku=line.sku,
            name=line.name,
            unit_price=line.unit_price,
            quantity=line.quantity,
        )
        for line in order.lines.all()
    )
    return OrderDetail(
        public_id=order.public_id,
        status=order.status,
        total_price=order.total_price,
        created_at=order.created_at,
        recipient_name=order.recipient_name,
        postal_code=order.postal_code,
        prefecture=order.prefecture,
        city=order.city,
        address_line=order.address_line,
        phone=order.phone,
        lines=lines,
    )
