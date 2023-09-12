from django.db.models import QuerySet
from rest_framework import mixins, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from shop.models import Cart, Order
from shop.serializers import CartSerializer, CreateOrderSerializer, OrderSerializer


class CartViewSet(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, GenericViewSet
):
    """
    CartViewSet is a viewset that provides the following actions:
    create, retrieve, destroy, list.
    All action is available only for the owner of the carts.
    """
    serializer_class = CartSerializer

    def get_queryset(self) -> QuerySet:
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer) -> None:
        serializer.save(user=self.request.user)


class OrderViewSet(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, GenericViewSet
):
    """
    OrderViewSet is a viewset that provides the following actions:
    create, retrieve, destroy, list.
    All action is available only for the owner of the carts and orders.
    """

    def get_queryset(self) -> QuerySet:
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer: CreateOrderSerializer) -> None:
        serializer.save(user=self.request.user)

    def get_serializer_class(self) -> CreateOrderSerializer | OrderSerializer:
        if self.action == 'create':
            return CreateOrderSerializer
        return OrderSerializer

    def create(self, request: Request, *args, **kwargs) -> Response:
        """
        Create an order from the cart.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = OrderSerializer(serializer.instance)
        return Response({
            "order_id": serializer.data.get("id"),
            "order_status": serializer.data.get("status"),
            "shelves": serializer.data.get("order_items")
        }, status=status.HTTP_201_CREATED)
