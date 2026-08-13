from decimal import Decimal

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response

from application.api.serializers.part import (
    CreatePartInputSerializer,
    PartListQuerySerializer,
    PartOutputSerializer,
    UpdatePartInputSerializer,
    part_output_payload,
)
from application.selectors.part import PartFilter, get_part, list_parts
from application.services.part import (
    UNSET,
    CreatePartInput,
    Unset,
    UpdatePartInput,
    create_part,
    update_part,
)


@api_view(["GET", "POST"])
@permission_classes([IsAdminUser])
def staff_part_list(request: Request) -> Response:
    if request.method == "POST":
        return staff_part_create(request)
    query = PartListQuerySerializer(data=request.query_params)
    query.is_valid(raise_exception=True)
    parts = list_parts(filter=PartFilter(category=query.validated_data.get("category")))
    output = PartOutputSerializer(
        [part_output_payload(part=part) for part in parts],
        many=True,
    )
    return Response(output.data)


def staff_part_create(request: Request) -> Response:
    serializer = CreatePartInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    part_id = create_part(
        input=CreatePartInput(
            sku=data["sku"],
            name=data["name"],
            category=data["category"],
            unit_price=data["unit_price"],
            stock_quantity=data["stock_quantity"],
            is_listed=data["is_listed"],
            socket=data["socket"],
            tdp_watts=data["tdp_watts"],
            memory_type=data["memory_type"],
            form_factor=data["form_factor"],
            memory_slot_count=data["memory_slot_count"],
            sata_port_count=data["sata_port_count"],
            m2_slot_count=data["m2_slot_count"],
            module_count=data["module_count"],
            capacity_gb=data["capacity_gb"],
            length_mm=data["length_mm"],
            interface=data["interface"],
            wattage=data["wattage"],
            max_gpu_length_mm=data["max_gpu_length_mm"],
            max_cooler_height_mm=data["max_cooler_height_mm"],
            height_mm=data["height_mm"],
        )
    )
    # Service は id だけ返す。表示は Selector で取り直す。
    part = get_part(part_id=part_id)
    output = PartOutputSerializer(part_output_payload(part=part))
    return Response(output.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PATCH"])
@permission_classes([IsAdminUser])
def staff_part_show(request: Request, part_id: int) -> Response:
    if request.method == "PATCH":
        return staff_part_update(request, part_id)
    part = get_part(part_id=part_id)
    output = PartOutputSerializer(part_output_payload(part=part))
    return Response(output.data)


def staff_part_update(request: Request, part_id: int) -> Response:
    serializer = UpdatePartInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    update_part(input=_update_input(part_id=part_id, values=serializer.validated_data))
    part = get_part(part_id=part_id)
    output = PartOutputSerializer(part_output_payload(part=part))
    return Response(output.data)


def _update_input(*, part_id: int, values: dict[str, object]) -> UpdatePartInput:
    # PATCH は送ったフィールドだけ変える。未送信は UNSET。
    return UpdatePartInput(
        part_id=part_id,
        sku=_present_str(values=values, field_name="sku"),
        name=_present_str(values=values, field_name="name"),
        category=_present_str(values=values, field_name="category"),
        unit_price=_present_decimal(values=values, field_name="unit_price"),
        stock_quantity=_present_int(values=values, field_name="stock_quantity"),
        is_listed=_present_bool(values=values, field_name="is_listed"),
        socket=_present_str(values=values, field_name="socket"),
        tdp_watts=_present_optional_int(values=values, field_name="tdp_watts"),
        memory_type=_present_str(values=values, field_name="memory_type"),
        form_factor=_present_str(values=values, field_name="form_factor"),
        memory_slot_count=_present_optional_int(
            values=values,
            field_name="memory_slot_count",
        ),
        sata_port_count=_present_optional_int(
            values=values,
            field_name="sata_port_count",
        ),
        m2_slot_count=_present_optional_int(values=values, field_name="m2_slot_count"),
        module_count=_present_optional_int(values=values, field_name="module_count"),
        capacity_gb=_present_optional_int(values=values, field_name="capacity_gb"),
        length_mm=_present_optional_int(values=values, field_name="length_mm"),
        interface=_present_str(values=values, field_name="interface"),
        wattage=_present_optional_int(values=values, field_name="wattage"),
        max_gpu_length_mm=_present_optional_int(
            values=values,
            field_name="max_gpu_length_mm",
        ),
        max_cooler_height_mm=_present_optional_int(
            values=values,
            field_name="max_cooler_height_mm",
        ),
        height_mm=_present_optional_int(values=values, field_name="height_mm"),
    )


def _present_str(*, values: dict[str, object], field_name: str) -> str | Unset:
    if field_name not in values:
        return UNSET
    value = values[field_name]
    return value if isinstance(value, str) else UNSET


def _present_int(*, values: dict[str, object], field_name: str) -> int | Unset:
    if field_name not in values:
        return UNSET
    value = values[field_name]
    return value if isinstance(value, int) else UNSET


def _present_bool(*, values: dict[str, object], field_name: str) -> bool | Unset:
    if field_name not in values:
        return UNSET
    value = values[field_name]
    return value if isinstance(value, bool) else UNSET


def _present_decimal(*, values: dict[str, object], field_name: str) -> Decimal | Unset:
    if field_name not in values:
        return UNSET
    value = values[field_name]
    if isinstance(value, Decimal):
        return value
    if isinstance(value, int):
        return Decimal(value)
    return UNSET


def _present_optional_int(
    *,
    values: dict[str, object],
    field_name: str,
) -> int | None | Unset:
    if field_name not in values:
        return UNSET
    value = values[field_name]
    if value is None or isinstance(value, int):
        return value
    return UNSET
