import pytest
from rest_framework.test import APIClient

from utils.factories import (
    ProductFactory, GlobalProductLimitFactory, RegionFactory, UserFactory, CartFactory,
    CartItemFactory
)


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def product(db):
    return ProductFactory()


@pytest.fixture
def global_limit(db):
    return GlobalProductLimitFactory()


@pytest.fixture
def region(db):
    return RegionFactory()


@pytest.fixture
def client(db, user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def cart_1_item(db, user, product, region):
    cart = CartFactory(user=user, region=region)
    CartItemFactory(product=product, cart=cart)
    return cart


@pytest.fixture
def cart_1_item_second_region(db, user, product):
    different_region = RegionFactory(name="OTHER")
    cart = CartFactory(user=user, region=different_region)
    CartItemFactory(product=product, cart=cart)
    return cart
