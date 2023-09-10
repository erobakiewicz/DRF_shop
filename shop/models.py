from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from shop.constants import CartStatuses, OrderStatuses, ErrorMessages
from shop.exceptions import (
    GlobalProductLimitObjectDoesNotExist
)


class GlobalProductLimit(models.Model):
    limit_size = models.IntegerField(
        verbose_name='product limit size',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = "Global product limit"

    def __str__(self) -> str:
        return f"Global product sold limit: {self.limit_size}"

    def save(self, *args, **kwargs) -> None:
        """
        Deletes all other objects and saves the current one thus making sure global limit is a singleton object.
        """
        self.__class__.objects.exclude(id=self.id).delete()
        super().save(*args, **kwargs)

    @classmethod
    def get_global_limit(cls) -> int:
        """
        Returns the global limit size.
        :return: global limit size or ObjectDoesNotExist exception
        """
        global_limit = cls.objects.first()

        if not global_limit:
            raise GlobalProductLimitObjectDoesNotExist(ErrorMessages.GLOBAL_LIMIT_NOT_SET)
        return global_limit.limit_size


class Region(models.Model):
    name = models.CharField(verbose_name="name", max_length=64)
    limit_size = models.IntegerField(verbose_name='product limit size')
    closed_access = models.BooleanField(verbose_name="closed access", default=False)
    unlimited_access = models.BooleanField(verbose_name="unlimited access", default=False)

    class Meta:
        verbose_name = "Region"
        verbose_name_plural = "Regions"

    def __str__(self) -> str:
        return f"Region {self.name}"

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        return super().save(*args, **kwargs)

    def clean(self) -> None:
        if self.closed_access and self.unlimited_access:
            raise ValidationError(ErrorMessages.REGION_ACCESS_ERROR)


class Shelf(models.Model):
    name = models.CharField(verbose_name="name", max_length=256)

    class Meta:
        verbose_name = "Shelf"
        verbose_name_plural = "Shelves"

    def __str__(self) -> str:
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="owner",
        on_delete=models.CASCADE
    )
    status = models.IntegerField(
        verbose_name="status",
        choices=CartStatuses.Choices,
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
    shelf = models.ForeignKey(
        Shelf,
        verbose_name="shelf",
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Cart items"

    def __str__(self) -> str:
        return self.shelf.name


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
        choices=OrderStatuses.Choices,
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
        Shelf,
        verbose_name="shelf",
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Order item"
        verbose_name_plural = "Order items"

    def __str__(self) -> str:
        return f"Order {self.order.id} shelf {self.item.name}"
