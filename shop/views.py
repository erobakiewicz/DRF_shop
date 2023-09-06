import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework import mixins
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from shop.exceptions import (
    ObjectDoesNotExistAPIException, GlobalLimitExceedException, RegionLimitExceedException,
    GlobalProductLimitObjectDoesNotExist
)
from shop.models import Cart, Region, Order, OrderItem
from shop.serializers import CartSerializer, CreateOrderSerializer, OrderSerializer


class CartViewSet(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, GenericViewSet
):
    """
    CartViewSet is a viewset that provides the following actions:
    create, retrieve, destroy, list.
    All action is available only for the owner of the carts.
    """
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderViewSet(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, GenericViewSet
):
    """
    OrderViewSet is a viewset that provides the following actions:
    create, retrieve, destroy, list.
    All action is available only for the owner of the carts and orders.
    """
    queryset = Order.objects.all()

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateOrderSerializer
        return OrderSerializer

    @staticmethod
    def get_create_response(order: Order):
        """
        Creates a response for the creation action.
        :param order: Order
        :return: REST Framework Response
        """
        serializer = OrderSerializer(order)
        return Response({
            "order_id": serializer.data.get("id"),
            "order_status": serializer.data.get("status"),
            "shelves": serializer.data.get("order_items")
        }, status=201)

    def create(self, request, *args, **kwargs):
        """
        Creates or get (if order for that day and that region already exists) an order from the cart.
        Validates the limits and closes the cart.
        :param request: Request
        :return: REST Framework Response or APIException
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            cart = Cart.objects.get(id=data.get('cart_id'))
        except ObjectDoesNotExist as exc:
            raise ObjectDoesNotExistAPIException(detail=exc)
        try:
            region = Region.objects.get(name=data.get('region'))
        except ObjectDoesNotExist as exc:
            raise ObjectDoesNotExistAPIException(detail=exc)
        with transaction.atomic():
            order = Order.objects.create(
                region=region,
                user=cart.user,
                created_at=datetime.date.today()
            )
            for cart_item in cart.cart_items.all():
                try:
                    OrderItem.objects.create(order=order, item=cart_item.shelf)
                except (
                        RegionLimitExceedException, GlobalLimitExceedException, GlobalProductLimitObjectDoesNotExist
                ) as exc:
                    raise ValidationError(exc)
            cart.status = Cart.Statuses.CLOSED
            cart.save(update_fields=["status"])
        return self.get_create_response(order=order)
