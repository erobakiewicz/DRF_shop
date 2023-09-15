from django.db.models import QuerySet
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from carts.models import Cart
from carts.serializers import CartSerializer


# Create your views here.
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
