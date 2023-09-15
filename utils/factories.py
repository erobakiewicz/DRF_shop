import factory
from django.contrib.auth.models import User

from faker import Factory as FakerFactory

from shop.models import GlobalProductLimit, Product, Region
from orders.models import Order, OrderItem
from carts.models import Cart, CartItem

faker = FakerFactory.create()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User


class GlobalProductLimitFactory(factory.django.DjangoModelFactory):
    limit_size = 3

    class Meta:
        model = GlobalProductLimit


class RegionFactory(factory.django.DjangoModelFactory):
    name = "EU"
    limit_size = 3

    class Meta:
        model = Region


class ProductFactory(factory.django.DjangoModelFactory):
    name = factory.LazyFunction(lambda: faker.name())

    class Meta:
        model = Product


class CartFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    region = factory.SubFactory(RegionFactory)

    class Meta:
        model = Cart


class CartItemFactory(factory.django.DjangoModelFactory):
    cart = factory.SubFactory(CartFactory)
    product = factory.SubFactory(ProductFactory)

    class Meta:
        model = CartItem


class OrderFactory(factory.django.DjangoModelFactory):
    region = factory.SubFactory(RegionFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = Order


class OrderItemFactory(factory.django.DjangoModelFactory):
    order = factory.SubFactory(OrderFactory)
    item = factory.SubFactory(ProductFactory)

    class Meta:
        model = OrderItem
