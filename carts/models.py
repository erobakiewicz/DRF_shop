from django.contrib.auth.models import User
from django.db import models

from utils.constants import CartStatuses
from shop.models import Region, Product


class Cart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="owner",
        on_delete=models.CASCADE
    )
    status = models.IntegerField(
        verbose_name="status",
        choices=CartStatuses.choices,
        default=CartStatuses.OPEN
    )
    region = models.ForeignKey(
        Region,
        verbose_name="cart region",
        related_name="region_carts",
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

    def __str__(self) -> str:
        return f"Cart of user {self.user} cart, id: {self.id}"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        verbose_name="cart",
        related_name="cart_items",
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        verbose_name="product",
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Cart items"

    def __str__(self) -> str:
        return self.product.name
