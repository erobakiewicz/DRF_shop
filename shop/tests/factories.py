import factory
from django.contrib.auth.models import User

from faker import Factory as FakerFactory

from shop.models import GlobalProductLimit, Order, OrderItem, Shelf, Region, CartItem, Cart

faker = FakerFactory.create()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User


class GlobalProductLimitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GlobalProductLimit

    limit_size = 3


class RegionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Region

    name = "EU"
    limit_size = 3


class ShelfFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Shelf

    name = factory.LazyFunction(lambda: faker.name())


class CartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cart

    user = factory.SubFactory(UserFactory)
    region = factory.SubFactory(RegionFactory)


class CartItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CartItem

    cart = factory.SubFactory(CartFactory)
    shelf = factory.SubFactory(ShelfFactory)


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    region = factory.SubFactory(RegionFactory)
    user = factory.SubFactory(UserFactory)


class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    item = factory.SubFactory(ShelfFactory)
