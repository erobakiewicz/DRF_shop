import datetime

from django.db import transaction
from django.db.models import QuerySet, Count, Sum, Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from carts.models import Cart
from orders.models import OrderItem, Order
from utils.constants import CartStatuses, ErrorMessages
from utils.exceptions import (
    GlobalProductLimitObjectDoesNotExist, GlobalLimitExceedException, RegionLimitExceedException
)
from shop.models import Region, GlobalProductLimit
from shop.serializers import ShelfSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    item = ShelfSerializer()

    class Meta:
        model = OrderItem
        fields = ['item']


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "region", "order_items", "status"]
        read_only_fields = ['status']


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.IntegerField()
    region = serializers.CharField(max_length=64)

    def create(self, validated_data: dict) -> Order:
        """
        Creates an order from the cart and validates the limits. Today's orders are locked in database until operation
        is finished. If the limits are exceeded, raises an exception and returns API response. Changes are rolled back.
        """
        cart = Cart.objects.get(id=validated_data.get('cart_id'))
        region = Region.objects.get(name=validated_data.get('region'))

        today_orders = Order.objects.select_for_update().filter(
            created_at=datetime.date.today()
        )
        with transaction.atomic():
            order = Order.objects.create(
                region=region,
                user=cart.user,
                created_at=datetime.date.today()
            )
            OrderItem.objects.bulk_create(
                objs=[OrderItem(order=order, item=cart_item.shelf) for cart_item in cart.cart_items.all()])
            try:
                self.validate_limits(order=order, today_orders=today_orders)
            except (
                    GlobalProductLimitObjectDoesNotExist, GlobalLimitExceedException, RegionLimitExceedException
            ) as exc:
                raise ValidationError(detail=exc.message, code=exc.code)
            cart.status = CartStatuses.CLOSED
            cart.save(update_fields=["status"])
        return order

    @staticmethod
    def validate_limits(order: Order, today_orders: QuerySet) -> None:
        """
        Validates the global and local limits. Today's orders including current one are counted and compared to the
        limits. If result is negative the limits are exceeded.
        Raises an exception if the limits are exceeded.
        """
        global_limit_size = GlobalProductLimit.get_global_limit()

        total_items_today = today_orders.annotate(
            items_count=Count('order_items'),
            region_items_count=Count("order_items", filter=Q(region=order.region))).aggregate(
            total_items=Sum('items_count'),
            region_items=Sum('region_items_count')
        )
        global_limit = global_limit_size - total_items_today['total_items']

        if global_limit < 0:
            raise GlobalLimitExceedException(ErrorMessages.GLOBAL_LIMIT_EXCEEDED)

        if not order.region.unlimited_access:
            ordered_items_count = total_items_today["region_items"]
            local_limit = order.region.limit_size - ordered_items_count

            if order.region.closed_access or local_limit < 0:
                raise RegionLimitExceedException(ErrorMessages.REGION_LIMIT_EXCEEDED.format(order.region.name))

    def validate(self, data: dict):
        """
        Validates the cart and order regions match.
        """
        if data['region'] != Cart.objects.get(id=data['cart_id']).region.name:
            raise serializers.ValidationError(ErrorMessages.ORDER_CART_REGIONS_MISMATCH)
        return data

    def validate_cart_id(self, value: int):
        """
        Validates if the cart belong to user.
        """
        if not Cart.objects.filter(id=value, user=self.context['request'].user).exists():
            raise serializers.ValidationError(ErrorMessages.CART_USER_MISMATCH)
        return value

    def validate_region(self, value: str):
        """
        Validates if the region exists.
        """
        if not Region.objects.filter(name=value).exists():
            raise serializers.ValidationError(ErrorMessages.REGION_DOES_NOT_EXIST)
        return value
