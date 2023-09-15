from django.contrib.auth.models import User
from django.db import models

from utils.constants import OrderStatuses
from shop.models import Region, Product


class Order(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="owner",
        on_delete=models.CASCADE
    )
    region = models.ForeignKey(
        Region,
        verbose_name="region",
        on_delete=models.CASCADE
    )
    status = models.IntegerField(
        verbose_name="status",
        choices=OrderStatuses.choices,
        default=OrderStatuses.PENDING
    )
    created_at = models.DateField(verbose_name="created at", auto_now_add=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self) -> str:
        return f"Order {self.id}, user {self.user}, region {self.region}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name="order",
        related_name="order_items",
        on_delete=models.CASCADE
    )
    item = models.ForeignKey(
        Product,
        verbose_name="product",
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Order item"
        verbose_name_plural = "Order items"

    def __str__(self) -> str:
        return f"Order {self.order.id} product {self.item.name}"
