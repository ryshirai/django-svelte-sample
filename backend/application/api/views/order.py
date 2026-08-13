from uuid import UUID

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from application.api.serializers.order import (
    CreateOrderInputSerializer,
    CreateOrderOutputSerializer,
    OrderListItemOutputSerializer,
    OrderOutputSerializer,
    order_output_payload,
)
from application.api.views.auth_user import authenticated_user_id
from application.selectors.order import (
    get_order_for_user,
    list_orders_for_user,
)
from application.services.order import CreateOrderInput, create_order


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def order_list(request: Request) -> Response:
    if request.method == "POST":
        return order_create(request)
    orders = list_orders_for_user(user_id=authenticated_user_id(request=request))
    output = OrderListItemOutputSerializer(orders, many=True)
    return Response(output.data)


def order_create(request: Request) -> Response:
    serializer = CreateOrderInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    public_id = create_order(
        input=CreateOrderInput(
            user_id=authenticated_user_id(request=request),
            part_ids=tuple(serializer.validated_data["part_ids"]),
            recipient_name=serializer.validated_data["recipient_name"],
            postal_code=serializer.validated_data["postal_code"],
            prefecture=serializer.validated_data["prefecture"],
            city=serializer.validated_data["city"],
            address_line=serializer.validated_data["address_line"],
            phone=serializer.validated_data["phone"],
        )
    )
    # Model は返さない。フロントは public_id で GET し直す。
    output = CreateOrderOutputSerializer({"public_id": public_id})
    return Response(output.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def order_show(request: Request, public_id: UUID) -> Response:
    order = get_order_for_user(
        public_id=public_id,
        user_id=authenticated_user_id(request=request),
    )
    output = OrderOutputSerializer(order_output_payload(order=order))
    return Response(output.data)
