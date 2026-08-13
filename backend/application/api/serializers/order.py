from typing import Any

from rest_framework import serializers


def order_output_payload(*, order: Any) -> dict[str, object]:
    return {
        "public_id": order.public_id,
        "status": order.status,
        "total_price": order.total_price,
        "created_at": order.created_at,
        "recipient_name": order.recipient_name,
        "postal_code": order.postal_code,
        "prefecture": order.prefecture,
        "city": order.city,
        "address_line": order.address_line,
        "phone": order.phone,
        "lines": [
            {
                "category": line.category,
                "sku": line.sku,
                "name": line.name,
                "unit_price": line.unit_price,
                "quantity": line.quantity,
            }
            for line in order.lines
        ],
    }


class CreateOrderInputSerializer(serializers.Serializer[Any]):
    # 決済は空配列を入力エラーにする。プレビューとは違う。
    part_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
    )
    recipient_name = serializers.CharField(max_length=64)
    postal_code = serializers.RegexField(regex=r"^[0-9]{7}$")
    prefecture = serializers.CharField(max_length=8)
    city = serializers.CharField(max_length=64)
    address_line = serializers.CharField(max_length=128)
    phone = serializers.RegexField(regex=r"^[0-9]{10,11}$")


class CreateOrderOutputSerializer(serializers.Serializer[Any]):
    public_id = serializers.UUIDField()


class OrderListItemOutputSerializer(serializers.Serializer[Any]):
    public_id = serializers.UUIDField()
    status = serializers.CharField()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=0)
    created_at = serializers.DateTimeField()


class OrderLineOutputSerializer(serializers.Serializer[Any]):
    category = serializers.CharField()
    sku = serializers.CharField()
    name = serializers.CharField()
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=0)
    quantity = serializers.IntegerField()


class OrderOutputSerializer(serializers.Serializer[Any]):
    public_id = serializers.UUIDField()
    status = serializers.CharField()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=0)
    created_at = serializers.DateTimeField()
    recipient_name = serializers.CharField()
    postal_code = serializers.CharField()
    prefecture = serializers.CharField()
    city = serializers.CharField()
    address_line = serializers.CharField()
    phone = serializers.CharField()
    lines = OrderLineOutputSerializer(many=True)
