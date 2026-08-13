from typing import Any

from rest_framework import serializers


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
