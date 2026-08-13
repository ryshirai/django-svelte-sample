from decimal import Decimal

from django.core.validators import MinValueValidator, RegexValidator
from django.db import models


class Part(models.Model):
    class Category(models.TextChoices):
        CPU = "cpu", "cpu"
        MOTHERBOARD = "motherboard", "motherboard"
        MEMORY = "memory", "memory"
        STORAGE = "storage", "storage"
        PSU = "psu", "psu"
        CASE = "case", "case"
        GPU = "gpu", "gpu"
        CPU_COOLER = "cpu_cooler", "cpu_cooler"

    sku = models.CharField(
        max_length=32,
        unique=True,
        validators=[RegexValidator(regex=r"^[A-Z0-9-]{3,32}$")],
    )
    name = models.CharField(max_length=120)
    category = models.CharField(max_length=16, choices=Category.choices)
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("1"))],
    )
    stock_quantity = models.PositiveIntegerField()
    is_listed = models.BooleanField(default=True)
    # カテゴリ外の属性。使わないときは空文字または NULL。
    socket = models.CharField(max_length=32, blank=True, default="")
    tdp_watts = models.PositiveIntegerField(null=True, blank=True)
    memory_type = models.CharField(max_length=16, blank=True, default="")
    form_factor = models.CharField(max_length=16, blank=True, default="")
    memory_slot_count = models.PositiveIntegerField(null=True, blank=True)
    sata_port_count = models.PositiveIntegerField(null=True, blank=True)
    m2_slot_count = models.PositiveIntegerField(null=True, blank=True)
    module_count = models.PositiveIntegerField(null=True, blank=True)
    capacity_gb = models.PositiveIntegerField(null=True, blank=True)
    length_mm = models.PositiveIntegerField(null=True, blank=True)
    interface = models.CharField(max_length=8, blank=True, default="")
    wattage = models.PositiveIntegerField(null=True, blank=True)
    max_gpu_length_mm = models.PositiveIntegerField(null=True, blank=True)
    max_cooler_height_mm = models.PositiveIntegerField(null=True, blank=True)
    height_mm = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(unit_price__gte=1),
                name="part_unit_price_gte_1",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    category__in=[
                        "cpu",
                        "motherboard",
                        "memory",
                        "storage",
                        "psu",
                        "case",
                        "gpu",
                        "cpu_cooler",
                    ]
                ),
                name="part_category_allowed",
            ),
        ]
