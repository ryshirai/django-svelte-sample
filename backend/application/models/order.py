import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models


class Order(models.Model):
    class Status(models.TextChoices):
        PAID = "paid", "paid"
        PREPARING = "preparing", "preparing"
        SHIPPED = "shipped", "shipped"
        CANCELLED = "cancelled", "cancelled"

    # 顧客向け識別子。内部 pk は顧客 URL に出さない。
    public_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    status = models.CharField(max_length=16, choices=Status.choices)
    recipient_name = models.CharField(max_length=64)
    postal_code = models.CharField(
        max_length=7,
        validators=[RegexValidator(regex=r"^[0-9]{7}$")],
    )
    prefecture = models.CharField(max_length=8)
    city = models.CharField(max_length=64)
    address_line = models.CharField(max_length=128)
    phone = models.CharField(
        max_length=13,
        validators=[RegexValidator(regex=r"^[0-9]{10,11}$")],
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("1"))],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(total_price__gte=1),
                name="order_total_price_gte_1",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    status__in=["paid", "preparing", "shipped", "cancelled"]
                ),
                name="order_status_allowed",
            ),
        ]
