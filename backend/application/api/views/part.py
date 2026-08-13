from typing import Any

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from application.api.serializers.part import (
    PartListQuerySerializer,
    PartOutputSerializer,
)
from application.models.part import Part
from application.selectors.part import PartFilter, get_listed_part, list_listed_parts


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def part_list(request: Request) -> Response:
    query = PartListQuerySerializer(data=request.query_params)
    query.is_valid(raise_exception=True)
    parts = list_listed_parts(
        filter=PartFilter(category=query.validated_data.get("category"))
    )
    output = PartOutputSerializer(
        [part_output_payload(part=part) for part in parts],
        many=True,
    )
    return Response(output.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def part_show(request: Request, part_id: int) -> Response:
    del request
    part = get_listed_part(part_id=part_id)
    output = PartOutputSerializer(part_output_payload(part=part))
    return Response(output.data)


def part_output_payload(*, part: Part) -> dict[str, Any]:
    return {
        "id": part.id,
        "sku": part.sku,
        "name": part.name,
        "category": part.category,
        "unit_price": part.unit_price,
        "stock_quantity": part.stock_quantity,
        "is_listed": part.is_listed,
        "socket": part.socket,
        "tdp_watts": part.tdp_watts,
        "memory_type": part.memory_type,
        "form_factor": part.form_factor,
        "memory_slot_count": part.memory_slot_count,
        "sata_port_count": part.sata_port_count,
        "m2_slot_count": part.m2_slot_count,
        "module_count": part.module_count,
        "capacity_gb": part.capacity_gb,
        "length_mm": part.length_mm,
        "interface": part.interface,
        "wattage": part.wattage,
        "max_gpu_length_mm": part.max_gpu_length_mm,
        "max_cooler_height_mm": part.max_cooler_height_mm,
        "height_mm": part.height_mm,
    }
