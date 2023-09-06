import datetime

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models

from shop.exceptions import (
    GlobalProductLimitObjectDoesNotExist, GlobalLimitExceedException, RegionLimitExceedException
)


class GlobalProductLimit(models.Model):
    limit_size = models.IntegerField(verbose_name='global product limit size', validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = "Global product limit"

    def __str__(self):
        return f"Global product sold limit: {self.limit_size}"

    def save(self, *args, **kwargs):
        """
        Deletes all other objects and saves the current one thus making sure global limit is a singleton object.
        """
        self.__class__.objects.exclude(id=self.id).delete()
        super().save(*args, **kwargs)

    @classmethod
    def get_global_limit(cls):
        """
        Returns the global limit size.
        :return: global limit size or ObjectDoesNotExist exception
        """
        global_limit = cls.objects.first()
        if not global_limit:
            raise GlobalProductLimitObjectDoesNotExist("Global limit not set.")
        return global_limit.limit_size


class Region(models.Model):
    name = models.CharField(verbose_name="region name", max_length=8)
    limit_size = models.IntegerField(verbose_name='region product limit size')
    close_region = models.BooleanField(verbose_name="close region", default=False)
    unlimited_access = models.BooleanField(verbose_name="unlimited", default=False)

    class Meta:
        verbose_name = "Region"
        verbose_name_plural = "Regions"

    def __str__(self):
        return (f"Region {self.name}: limit {self.limit_size}, closed: {self.close_region}, "
                f"unlimited: {self.unlimited_access}")


class Shelf(models.Model):
    name = models.CharField(verbose_name="shelf name", max_length=256)

    class Meta:
        verbose_name = "Shelf"
        verbose_name_plural = "Shelves"

    def __str__(self):
        return self.name


class Cart(models.Model):
    class Statuses(models.TextChoices):
        OPEN = "OP", "OPEN"
        CLOSED = "CL", "CLOSED"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(verbose_name="cart status", choices=Statuses.choices, default=Statuses.OPEN)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

    def __str__(self):
        return f"Cart of user {self.user} cart, id: {self.id}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="cart_items", on_delete=models.CASCADE)
    shelf = models.ForeignKey(Shelf, verbose_name="shelf name", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Cart items"

    def __str__(self):
        return self.shelf.name


class Order(models.Model):
    class Statuses(models.TextChoices):
        PENDING = "PD", "PENDING"
        COMPLETED = "CP", "COMPLETED"
        CANCELED = "CL", "CANCELLED"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    status = models.CharField(verbose_name="order status", choices=Statuses.choices, default=Statuses.PENDING)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return f"Order {self.id}, user {self.user}, region {self.region}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    item = models.ForeignKey(Shelf, on_delete=models.CASCADE, verbose_name="shelf")

    class Meta:
        verbose_name = "Order item"
        verbose_name_plural = "Order items"

    def __str__(self):
        return f"Order {self.order.id} shelf {self.item.name}"

    def save(self, *args, **kwargs):
        """
        Validates the limits and saves the item.
        """
        self.validate_global_daily_limit()

        if not self.order.region.unlimited_access:
            self.validate_regional_daily_limit(region=self.order.region)
        super().save()

    @classmethod
    def validate_global_daily_limit(cls):
        """
        Checks if the global limit is exceeded for today.
        :return: None or APIException
        """
        total_items_today = cls.objects.filter(order__created_at=datetime.date.today())
        global_limit_size = GlobalProductLimit.get_global_limit()
        if total_items_today:
            global_limit = global_limit_size - total_items_today.count()
        else:
            global_limit = global_limit_size

        if global_limit <= 0:
            raise GlobalLimitExceedException("Global limit exceeded.")

    def validate_regional_daily_limit(self, region: Order.region):
        """
        Checks if the region is closed or the limit is exceeded for today.
        :param region: Region
        :return: None or APIException
        """
        ordered_items_count = OrderItem.objects.filter(
            order__created_at=datetime.date.today(),
            order__region=region
        ).count()
        local_limit = region.limit_size - ordered_items_count

        if region.close_region or local_limit <= 0:
            raise RegionLimitExceedException(f"Region {self.order.region.name}: closed or limit exceeded.")
