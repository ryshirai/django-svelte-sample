from dataclasses import dataclass
from decimal import Decimal
from enum import Enum, auto
from typing import Any

from django.db import IntegrityError, transaction

from application.errors.part import PartNotFoundError, PartSkuAlreadyUsedError
from application.models.part import Part
from application.validators.part_attributes import (
    PartAttributeValues,
    validate_part_attributes,
)

PART_VALUE_FIELDS = (
    "sku",
    "name",
    "category",
    "unit_price",
    "stock_quantity",
    "is_listed",
    "socket",
    "tdp_watts",
    "memory_type",
    "form_factor",
    "memory_slot_count",
    "sata_port_count",
    "m2_slot_count",
    "module_count",
    "capacity_gb",
    "length_mm",
    "interface",
    "wattage",
    "max_gpu_length_mm",
    "max_cooler_height_mm",
    "height_mm",
)


class Unset(Enum):
    # PATCH で「未送信」と「明示的な null」を区別する番兵。
    TOKEN = auto()


UNSET = Unset.TOKEN


@dataclass(frozen=True, slots=True, kw_only=True)
class CreatePartInput:
    sku: str
    name: str
    category: str
    unit_price: Decimal
    stock_quantity: int
    is_listed: bool
    socket: str
    tdp_watts: int | None
    memory_type: str
    form_factor: str
    memory_slot_count: int | None
    sata_port_count: int | None
    m2_slot_count: int | None
    module_count: int | None
    capacity_gb: int | None
    length_mm: int | None
    interface: str
    wattage: int | None
    max_gpu_length_mm: int | None
    max_cooler_height_mm: int | None
    height_mm: int | None


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdatePartInput:
    part_id: int
    sku: str | Unset = UNSET
    name: str | Unset = UNSET
    category: str | Unset = UNSET
    unit_price: Decimal | Unset = UNSET
    stock_quantity: int | Unset = UNSET
    is_listed: bool | Unset = UNSET
    socket: str | Unset = UNSET
    tdp_watts: int | None | Unset = UNSET
    memory_type: str | Unset = UNSET
    form_factor: str | Unset = UNSET
    memory_slot_count: int | None | Unset = UNSET
    sata_port_count: int | None | Unset = UNSET
    m2_slot_count: int | None | Unset = UNSET
    module_count: int | None | Unset = UNSET
    capacity_gb: int | None | Unset = UNSET
    length_mm: int | None | Unset = UNSET
    interface: str | Unset = UNSET
    wattage: int | None | Unset = UNSET
    max_gpu_length_mm: int | None | Unset = UNSET
    max_cooler_height_mm: int | None | Unset = UNSET
    height_mm: int | None | Unset = UNSET


@transaction.atomic
def create_part(*, input: CreatePartInput) -> int:
    validate_part_attributes(values=_attributes_from_create(input=input))
    part = Part(
        sku=input.sku,
        name=input.name,
        category=input.category,
        unit_price=input.unit_price,
        stock_quantity=input.stock_quantity,
        is_listed=input.is_listed,
        socket=input.socket,
        tdp_watts=input.tdp_watts,
        memory_type=input.memory_type,
        form_factor=input.form_factor,
        memory_slot_count=input.memory_slot_count,
        sata_port_count=input.sata_port_count,
        m2_slot_count=input.m2_slot_count,
        module_count=input.module_count,
        capacity_gb=input.capacity_gb,
        length_mm=input.length_mm,
        interface=input.interface,
        wattage=input.wattage,
        max_gpu_length_mm=input.max_gpu_length_mm,
        max_cooler_height_mm=input.max_cooler_height_mm,
        height_mm=input.height_mm,
    )
    try:
        part.save()
    except IntegrityError as error:
        raise PartSkuAlreadyUsedError() from error
    return part.id


@transaction.atomic
def update_part(*, input: UpdatePartInput) -> int:
    try:
        part = Part.objects.select_for_update().get(pk=input.part_id)
    except Part.DoesNotExist as error:
        raise PartNotFoundError() from error
    changed = _apply_part_updates(part=part, input=input)
    validate_part_attributes(values=_attributes_from_part(part=part))
    try:
        part.save(update_fields=[*changed, "updated_at"])
    except IntegrityError as error:
        raise PartSkuAlreadyUsedError() from error
    return part.id


def _attributes_from_create(*, input: CreatePartInput) -> PartAttributeValues:
    return PartAttributeValues(
        category=input.category,
        socket=input.socket,
        tdp_watts=input.tdp_watts,
        memory_type=input.memory_type,
        form_factor=input.form_factor,
        memory_slot_count=input.memory_slot_count,
        sata_port_count=input.sata_port_count,
        m2_slot_count=input.m2_slot_count,
        module_count=input.module_count,
        capacity_gb=input.capacity_gb,
        length_mm=input.length_mm,
        interface=input.interface,
        wattage=input.wattage,
        max_gpu_length_mm=input.max_gpu_length_mm,
        max_cooler_height_mm=input.max_cooler_height_mm,
        height_mm=input.height_mm,
    )


def _attributes_from_part(*, part: Part) -> PartAttributeValues:
    return PartAttributeValues(
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


def _apply_part_updates(*, part: Part, input: UpdatePartInput) -> list[str]:
    changed: list[str] = []
    for field_name in PART_VALUE_FIELDS:
        value: Any = getattr(input, field_name)
        if value is UNSET:
            continue
        setattr(part, field_name, value)
        changed.append(field_name)
    return changed
