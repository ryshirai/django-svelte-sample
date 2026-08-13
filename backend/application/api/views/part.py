from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from application.api.serializers.part import (
    PartListQuerySerializer,
    PartOutputSerializer,
    part_output_payload,
)
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
