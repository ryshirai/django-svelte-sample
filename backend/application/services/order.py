from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from django.db import transaction

from application.errors.configuration import CONFIGURATION_ERROR_BY_CODE
from application.errors.order import (
    OrderInsufficientStockError,
    OrderInvalidStatusTransitionError,
    OrderNotFoundError,
    OrderPartUnlistedError,
)
from application.errors.part import PartNotFoundError
from application.models.order import Order
from application.models.order_line import OrderLine
from application.models.part import Part
from application.validators.pc_configuration import (
    ConfigurationPart,
    validate_pc_configuration,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateOrderInput:
    user_id: int
    part_ids: tuple[int, ...]
    recipient_name: str
    postal_code: str
    prefecture: str
    city: str
    address_line: str
    phone: str


@dataclass(frozen=True, slots=True, kw_only=True)
class OrderPublicIdInput:
    public_id: UUID


@transaction.atomic
def create_order(*, input: CreateOrderInput) -> UUID:
    parts = _lock_parts(part_ids=input.part_ids)
    _ensure_parts_purchasable(parts=parts)
    _ensure_configuration(parts=parts)
    _decrement_stock(parts=parts)
    order = _insert_order(input=input, parts=parts)
    # View へは public_id だけ返す。Model を渡して mutation させない。
    return order.public_id


@transaction.atomic
def prepare_order(*, input: OrderPublicIdInput) -> None:
    # paid → preparing。それ以外は invalid_status_transition。
    order = _lock_order(public_id=input.public_id)
    if order.status != Order.Status.PAID:
        raise OrderInvalidStatusTransitionError()
    order.status = Order.Status.PREPARING
    order.save(update_fields=["status", "updated_at"])


@transaction.atomic
def ship_order(*, input: OrderPublicIdInput) -> None:
    # preparing → shipped。shipped からは動かない。
    order = _lock_order(public_id=input.public_id)
    if order.status != Order.Status.PREPARING:
        raise OrderInvalidStatusTransitionError()
    order.status = Order.Status.SHIPPED
    order.save(update_fields=["status", "updated_at"])


@transaction.atomic
def cancel_order(*, input: OrderPublicIdInput) -> None:
    # paid / preparing → cancelled。shipped / cancelled からは動かない。
    order = _lock_order(public_id=input.public_id)
    if order.status not in {Order.Status.PAID, Order.Status.PREPARING}:
        raise OrderInvalidStatusTransitionError()
    _restore_stock(order=order)
    order.status = Order.Status.CANCELLED
    order.save(update_fields=["status", "updated_at"])


def _lock_parts(*, part_ids: tuple[int, ...]) -> list[Part]:
    # 複数行ロックは id 昇順で固定し、デッドロックを避ける。
    unique_ids = sorted(set(part_ids))
    parts = list(
        Part.objects.select_for_update().filter(pk__in=unique_ids).order_by("id")
    )
    if len(parts) != len(unique_ids):
        # 1 件でも欠けていれば part.not_found。どれが欠けたかは出さない。
        raise PartNotFoundError()
    return parts


def _ensure_parts_purchasable(*, parts: list[Part]) -> None:
    for part in parts:
        # 未掲載と在庫不足は別 code。どちらも details.sku を付ける。
        if not part.is_listed:
            raise OrderPartUnlistedError(details={"sku": part.sku})
        if part.stock_quantity < 1:
            raise OrderInsufficientStockError(details={"sku": part.sku})


def _ensure_configuration(*, parts: list[Part]) -> None:
    issues = validate_pc_configuration(
        parts=tuple(_to_configuration_part(part=part) for part in parts)
    )
    if not issues:
        return
    # HTTP の code は先頭 issue。details に全件を入れる。
    first = issues[0]
    error_class = CONFIGURATION_ERROR_BY_CODE[first.code]
    raise error_class(
        details={
            "issues": [
                {"code": issue.code, "details": issue.details} for issue in issues
            ]
        }
    )


def _decrement_stock(*, parts: list[Part]) -> None:
    for part in parts:
        part.stock_quantity -= 1
        part.save(update_fields=["stock_quantity", "updated_at"])


def _insert_order(*, input: CreateOrderInput, parts: list[Part]) -> Order:
    # 合計は現在の Part.unit_price。クライアントの金額は見ない。
    total = sum((part.unit_price for part in parts), start=Decimal("0"))
    order = Order.objects.create(
        user_id=input.user_id,
        status=Order.Status.PAID,  # 作成時点で paid。ドラフト行は作らない。
        recipient_name=input.recipient_name,
        postal_code=input.postal_code,
        prefecture=input.prefecture,
        city=input.city,
        address_line=input.address_line,
        phone=input.phone,
        total_price=total,
    )
    for part in parts:
        # sku / name / unit_price は注文時点のスナップショット。
        OrderLine.objects.create(
            order=order,
            part=part,
            category=part.category,
            sku=part.sku,
            name=part.name,
            unit_price=part.unit_price,
            quantity=1,
        )
    return order


def _lock_order(*, public_id: UUID) -> Order:
    try:
        return Order.objects.select_for_update().get(public_id=public_id)
    except Order.DoesNotExist as error:
        raise OrderNotFoundError() from error


def _restore_stock(*, order: Order) -> None:
    # create_order と同じく part id 昇順でロックする。
    part_ids = sorted(order.lines.values_list("part_id", flat=True))
    parts = Part.objects.select_for_update().filter(pk__in=part_ids).order_by("id")
    for part in parts:
        part.stock_quantity += 1
        part.save(update_fields=["stock_quantity", "updated_at"])


def _to_configuration_part(*, part: Part) -> ConfigurationPart:
    return ConfigurationPart(
        category=part.category,
        socket=part.socket,
        tdp_watts=part.tdp_watts,
        memory_type=part.memory_type,
        form_factor=part.form_factor,
        memory_slot_count=part.memory_slot_count,
        sata_port_count=part.sata_port_count,
        m2_slot_count=part.m2_slot_count,
        module_count=part.module_count,
        capacity_gb=part.capacity_gb,
        length_mm=part.length_mm,
        interface=part.interface,
        wattage=part.wattage,
        max_gpu_length_mm=part.max_gpu_length_mm,
        max_cooler_height_mm=part.max_cooler_height_mm,
        height_mm=part.height_mm,
    )
