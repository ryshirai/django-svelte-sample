from typing import Any

from rest_framework import serializers

from application.models.part import Part


class PartOutputSerializer(serializers.Serializer[Any]):
    id = serializers.IntegerField()
    sku = serializers.CharField()
    name = serializers.CharField()
    category = serializers.CharField()
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=0)
    stock_quantity = serializers.IntegerField()
    is_listed = serializers.BooleanField()
    socket = serializers.CharField(allow_blank=True)
    tdp_watts = serializers.IntegerField(allow_null=True)
    memory_type = serializers.CharField(allow_blank=True)
    form_factor = serializers.CharField(allow_blank=True)
    memory_slot_count = serializers.IntegerField(allow_null=True)
    sata_port_count = serializers.IntegerField(allow_null=True)
    m2_slot_count = serializers.IntegerField(allow_null=True)
    module_count = serializers.IntegerField(allow_null=True)
    capacity_gb = serializers.IntegerField(allow_null=True)
    length_mm = serializers.IntegerField(allow_null=True)
    interface = serializers.CharField(allow_blank=True)
    wattage = serializers.IntegerField(allow_null=True)
    max_gpu_length_mm = serializers.IntegerField(allow_null=True)
    max_cooler_height_mm = serializers.IntegerField(allow_null=True)
    height_mm = serializers.IntegerField(allow_null=True)


class CreatePartInputSerializer(serializers.Serializer[Any]):
    sku = serializers.RegexField(regex=r"^[A-Z0-9-]{3,32}$", max_length=32)
    name = serializers.CharField(max_length=120)
    category = serializers.ChoiceField(choices=Part.Category.choices)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=0, min_value=1)
    stock_quantity = serializers.IntegerField(min_value=0)
    is_listed = serializers.BooleanField()
    socket = serializers.CharField(max_length=32, allow_blank=True)
    tdp_watts = serializers.IntegerField(min_value=0, allow_null=True)
    memory_type = serializers.CharField(max_length=16, allow_blank=True)
    form_factor = serializers.CharField(max_length=16, allow_blank=True)
    memory_slot_count = serializers.IntegerField(min_value=0, allow_null=True)
    sata_port_count = serializers.IntegerField(min_value=0, allow_null=True)
    m2_slot_count = serializers.IntegerField(min_value=0, allow_null=True)
    module_count = serializers.IntegerField(min_value=0, allow_null=True)
    capacity_gb = serializers.IntegerField(min_value=0, allow_null=True)
    length_mm = serializers.IntegerField(min_value=0, allow_null=True)
    interface = serializers.CharField(max_length=8, allow_blank=True)
    wattage = serializers.IntegerField(min_value=0, allow_null=True)
    max_gpu_length_mm = serializers.IntegerField(min_value=0, allow_null=True)
    max_cooler_height_mm = serializers.IntegerField(min_value=0, allow_null=True)
    height_mm = serializers.IntegerField(min_value=0, allow_null=True)


class UpdatePartInputSerializer(serializers.Serializer[Any]):
    sku = serializers.RegexField(
        regex=r"^[A-Z0-9-]{3,32}$",
        max_length=32,
        required=False,
    )
    name = serializers.CharField(max_length=120, required=False)
    category = serializers.ChoiceField(choices=Part.Category.choices, required=False)
    unit_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=0,
        min_value=1,
        required=False,
    )
    stock_quantity = serializers.IntegerField(min_value=0, required=False)
    is_listed = serializers.BooleanField(required=False)
    socket = serializers.CharField(max_length=32, allow_blank=True, required=False)
    tdp_watts = serializers.IntegerField(min_value=0, allow_null=True, required=False)
    memory_type = serializers.CharField(max_length=16, allow_blank=True, required=False)
    form_factor = serializers.CharField(max_length=16, allow_blank=True, required=False)
    memory_slot_count = serializers.IntegerField(
        min_value=0,
        allow_null=True,
        required=False,
    )
    sata_port_count = serializers.IntegerField(
        min_value=0,
        allow_null=True,
        required=False,
    )
    m2_slot_count = serializers.IntegerField(
        min_value=0,
        allow_null=True,
        required=False,
    )
    module_count = serializers.IntegerField(
        min_value=0,
        allow_null=True,
        required=False,
    )
    capacity_gb = serializers.IntegerField(
        min_value=0,
        allow_null=True,
        required=False,
    )
    length_mm = serializers.IntegerField(
        min_value=0,
        allow_null=True,
        required=False,
    )
    interface = serializers.CharField(max_length=8, allow_blank=True, required=False)
    wattage = serializers.IntegerField(min_value=0, allow_null=True, required=False)
    max_gpu_length_mm = serializers.IntegerField(
        min_value=0,
        allow_null=True,
        required=False,
    )
    max_cooler_height_mm = serializers.IntegerField(
        min_value=0,
        allow_null=True,
        required=False,
    )
    height_mm = serializers.IntegerField(min_value=0, allow_null=True, required=False)


class PartListQuerySerializer(serializers.Serializer[Any]):
    category = serializers.ChoiceField(choices=Part.Category.choices, required=False)
