import pytest

from shop.tests.factories import (
    ShelfFactory, GlobalProductLimitFactory, RegionFactory, UserFactory, OrderItemFactory, OrderFactory, CartFactory,
    CartItemFactory
)
from rest_framework.test import APIClient


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def shelf(db):
    return ShelfFactory()


@pytest.fixture
def global_limit(db):
    return GlobalProductLimitFactory()


@pytest.fixture
def local_limit(db):
    return RegionFactory()


@pytest.fixture
def client(db, user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def cart_1_item(db, user, shelf, local_limit):
    cart = CartFactory(user=user, region=local_limit)
    CartItemFactory(shelf=shelf, cart=cart)
    return cart


@pytest.fixture
def cart_1_item_different_region(db, user, shelf):
    different_region = RegionFactory(name="OTHER")
    cart = CartFactory(user=user, region=different_region)
    CartItemFactory(shelf=shelf, cart=cart)
    return cart


@pytest.fixture
def order_with_3_items(db, user, local_limit):
    order = OrderFactory(user=user, region=local_limit)
    OrderItemFactory.create_batch(3, order=order)
    return order
