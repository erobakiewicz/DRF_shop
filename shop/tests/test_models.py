import pytest
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from shop.models import GlobalProductLimit
from shop.tests.factories import OrderItemFactory, RegionFactory, OrderFactory


def test_cannot_create_two_global_limits(db, get_global_limit):
    GlobalProductLimit.objects.create(limit_size=5)
    assert GlobalProductLimit.objects.all().count() == 1


def test_get_global_limit_does_not_exist(db):
    with pytest.raises(ObjectDoesNotExist) as exc:
        GlobalProductLimit.get_global_limit()
        assert exc.value == "Global limit not set!"


def test_cannot_create_order_above_global_limit(db, get_global_limit, order_with_3_items):
    with pytest.raises(ValidationError) as exc:
        OrderItemFactory(order=order_with_3_items)
        assert exc.value == "Global limit exceeded."


def test_cannot_create_order_above_global_limit_when_local_allows_orders(
        db,
        get_global_limit,
        get_local_limit,
        order_with_3_items
):
    get_local_limit.limit_size = 99
    get_local_limit.save(update_fields=['limit_size'])
    with pytest.raises(ValidationError) as exc:
        OrderItemFactory(order=order_with_3_items)
        assert exc.value == "Global limit exceeded."


def test_cannot_create_order_above_local_limit(db, get_global_limit, get_local_limit, order_with_3_items):
    get_local_limit.limit_size = 1
    get_local_limit.save(update_fields=['limit_size'])

    with pytest.raises(ValidationError) as exc:
        OrderItemFactory(order=order_with_3_items)
        assert exc.value == 'Local EU: closed or limit exceeded.'


def test_cannot_create_order_closed_region(db, get_global_limit):
    region_closed = RegionFactory(close_region=True)
    order = OrderFactory(region=region_closed)
    with pytest.raises(ValidationError) as exc:
        OrderItemFactory(order=order)
        assert exc.value == 'Local EU: closed or limit exceeded.'


def test_region_unlimited_access_bypass_local_limit(db, get_global_limit, get_local_limit, order_with_3_items):
    get_global_limit.limit_size = 99
    get_global_limit.save(update_fields=['limit_size'])
    get_local_limit.unlimited_access = True
    get_local_limit.save(update_fields=['unlimited_access'])

    assert get_local_limit.limit_size == 3

    OrderItemFactory(order=order_with_3_items)
    assert order_with_3_items.order_items.all().count() == 4


def test_region_unlimited_access_not_bypass_global_limit(db, get_global_limit, get_local_limit, order_with_3_items):
    get_local_limit.unlimited_access = True
    get_local_limit.save(update_fields=['unlimited_access'])

    with pytest.raises(ValidationError) as exc:
        OrderItemFactory(order=order_with_3_items)
        assert exc.value == "Global limit exceeded."
