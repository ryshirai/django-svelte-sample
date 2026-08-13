from uuid import UUID

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response

from application.api.serializers.order import (
    OrderListItemOutputSerializer,
    OrderOutputSerializer,
)
from application.api.views.order import order_payload
from application.selectors.order import get_order, list_orders
from application.services.order import (
    OrderPublicIdInput,
    cancel_order,
    prepare_order,
    ship_order,
)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def staff_order_list(request: Request) -> Response:
    del request
    output = OrderListItemOutputSerializer(list_orders(), many=True)
    return Response(output.data)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def staff_order_show(request: Request, public_id: UUID) -> Response:
    del request
    order = get_order(public_id=public_id)
    output = OrderOutputSerializer(order_payload(order=order))
    return Response(output.data)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def staff_order_prepare(request: Request, public_id: UUID) -> Response:
    del request
    prepare_order(input=OrderPublicIdInput(public_id=public_id))
    return Response(status=204)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def staff_order_ship(request: Request, public_id: UUID) -> Response:
    del request
    ship_order(input=OrderPublicIdInput(public_id=public_id))
    return Response(status=204)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def staff_order_cancel(request: Request, public_id: UUID) -> Response:
    del request
    cancel_order(input=OrderPublicIdInput(public_id=public_id))
    return Response(status=204)
