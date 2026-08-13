from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from application.models.part import Part


class OrderLine(models.Model):
    order = models.ForeignKey(
        "application.Order",
        on_delete=models.CASCADE,
        related_name="lines",
    )
    # 表示はスナップショット。part は参照とキャンセル時の在庫戻し用。
    part = models.ForeignKey(Part, on_delete=models.PROTECT, related_name="order_lines")
    category = models.CharField(max_length=16, choices=Part.Category.choices)
    sku = models.CharField(max_length=32)
    name = models.CharField(max_length=120)
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("1"))],
    )
    quantity = models.PositiveSmallIntegerField(default=1)

    class Meta:
        constraints = [
            # 1 注文につき各カテゴリ最大 1。
            models.UniqueConstraint(
                fields=["order", "category"],
                name="order_line_unique_category_per_order",
            ),
            models.CheckConstraint(
                condition=models.Q(quantity=1),
                name="order_line_quantity_is_1",
            ),
            models.CheckConstraint(
                condition=models.Q(unit_price__gte=1),
                name="order_line_unit_price_gte_1",
            ),
        ]
