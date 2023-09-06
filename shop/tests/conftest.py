import pytest

from shop.tests.factories import (
    ShelfFactory, GlobalProductLimitFactory, RegionFactory, UserFactory, OrderItemFactory, OrderFactory, CartFactory,
    CartItemFactory
)
from rest_framework.test import APIClient


@pytest.fixture
def get_user(db):
    return UserFactory()


@pytest.fixture
def get_shelf(db):
    return ShelfFactory()


@pytest.fixture
def get_global_limit(db):
    return GlobalProductLimitFactory()


@pytest.fixture
def get_local_limit(db):
    return RegionFactory()


@pytest.fixture
def get_client(db, get_user):
    client = APIClient()
    client.force_authenticate(user=get_user)
    return client


@pytest.fixture
def cart_1_item(db, get_user, get_shelf, get_local_limit):
    cart = CartFactory(user=get_user, region=get_local_limit)
    CartItemFactory(shelf=get_shelf, cart=cart)
    return cart


@pytest.fixture
def cart_1_item_different_region(db, get_user, get_shelf):
    different_region = RegionFactory(name="OTHER")
    cart = CartFactory(user=get_user, region=different_region)
    CartItemFactory(shelf=get_shelf, cart=cart)
    return cart


@pytest.fixture
def order_with_3_items(db, get_user, get_local_limit):
    order = OrderFactory(user=get_user, region=get_local_limit)
    OrderItemFactory(order=order)
    OrderItemFactory(order=order)
    OrderItemFactory(order=order)
    return order
