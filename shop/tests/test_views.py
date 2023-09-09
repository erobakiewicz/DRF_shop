import datetime

from django.urls import reverse
from freezegun import freeze_time
from rest_framework import status

from shop.constants import CartStatuses, OrderStatuses
from shop.models import Order
from shop.tests.factories import CartItemFactory


def test_add_item_to_cart(db, client, shelf, local_limit):
    data = {
        "region": local_limit.id,
        "cart_items": [
            {
                "shelf": shelf.id
            }
        ]
    }

    response = client.post(path=reverse("api:cart-list"), data=data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    expected_shelf = shelf.id
    assert response.data.get("status") == CartStatuses.OPEN
    assert response.data.get("cart_items")[0].get("shelf") == expected_shelf


def test_cannot_add_non_existing_item_to_cart(db, client, local_limit):
    data = {
        "region": local_limit.id,
        "cart_items": [
            {
                "shelf": 12345
            }
        ]
    }

    response = client.post(path=reverse("api:cart-list"), data=data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data.get("cart_items")[0].get("shelf")[0] == 'Invalid pk "12345" - object does not exist.'


def test_cannot_add_item_to_cart_non_existing_region(db, client, shelf):
    data = {
        "region": 12345,
        "cart_items": [
            {
                "shelf": shelf.id
            }
        ]
    }

    response = client.post(path=reverse("api:cart-list"), data=data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data.get("region")[0] == 'Invalid pk "12345" - object does not exist.'


def test_create_order_from_cart(
        db, user, client, shelf, global_limit, local_limit, cart_1_item
):
    response = client.post(
        path=reverse("api:order-list"),
        data={"cart_id": cart_1_item.id, "region": local_limit.name}
    )

    assert response.status_code == status.HTTP_201_CREATED
    expected_order = Order.objects.get(user=user)
    assert response.data.get("order_id") == expected_order.id
    assert response.data.get("order_status") == OrderStatuses.PENDING
    assert expected_order.region.name == local_limit.name
    assert response.data.get("shelves")[0].get("item").get("name") == shelf.name
    cart_1_item.refresh_from_db()
    assert cart_1_item.status == CartStatuses.CLOSED


def test_cannot_create_order_from_non_existing_cart(db, client, local_limit):
    response = client.post(
        path=reverse("api:order-list"),
        data={"cart_id": 12345, "region": local_limit.name}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data.get("cart_id")[0] == "Cart does not belong to user or does not exist."


def test_cannot_create_order_from_non_existing_region(
        db, user, client, shelf, global_limit, local_limit, cart_1_item
):
    response = client.post(path=reverse("api:order-list"), data={"cart_id": cart_1_item.id, "region": "Mordor"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data.get("region")[0] == "Region does not exist."


def test_cannot_create_order_from_cart_global_limit_not_set(
        db, user, client, shelf, local_limit, cart_1_item
):
    response = client.post(
        path=reverse("api:order-list"),
        data={"cart_id": cart_1_item.id, "region": local_limit.name}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data[0] == 'Global limit not set.'


def test_cannot_create_order_from_cart_global_limit_1_local_limit_3(
        db, user, client, shelf, global_limit, local_limit, cart_1_item,
):
    global_limit.limit_size = 1
    global_limit.save(update_fields=['limit_size'])
    CartItemFactory(shelf=shelf, cart=cart_1_item)

    response = client.post(
        path=reverse("api:order-list"),
        data={"cart_id": cart_1_item.id, "region": local_limit.name}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert str(response.data[0]) == "['Global limit exceeded.']"


def test_cannot_create_order_from_cart_local_limit_1_global_limit_3(
        db, user, client, shelf, global_limit, local_limit, cart_1_item
):
    CartItemFactory(shelf=shelf, cart=cart_1_item)

    local_limit.limit_size = 1
    local_limit.save(update_fields=['limit_size'])

    response = client.post(
        path=reverse("api:order-list"),
        data={"cart_id": cart_1_item.id, "region": local_limit.name}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert str(response.data[0]) == "['Region EU: closed or limit exceeded.']"


def test_create_order_from_cart_first_region_exceed_different_region_allow(
        db, user, client, shelf, global_limit, local_limit, cart_1_item_different_region,
        cart_1_item
):
    CartItemFactory(shelf=shelf, cart=cart_1_item)

    local_limit.limit_size = 1
    local_limit.save(update_fields=['limit_size'])
    response = client.post(
        path=reverse("api:order-list"),
        data={"cart_id": cart_1_item.id, "region": local_limit.name}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert str(response.data[0]) == "['Region EU: closed or limit exceeded.']"

    response = client.post(
        path=reverse("api:order-list"),
        data={"cart_id": cart_1_item_different_region.id, "region": cart_1_item_different_region.region.name}
    )

    assert response.status_code == status.HTTP_201_CREATED


def test_create_order_first_day_global_limit_exceeded_second_day_renewed(
        db, user, client, shelf, global_limit, local_limit,
        cart_1_item
):
    CartItemFactory(shelf=shelf, cart=cart_1_item)

    response = client.post(
        path=reverse("api:order-list"),
        data={"cart_id": cart_1_item.id, "region": local_limit.name}
    )

    assert response.status_code == status.HTTP_201_CREATED

    response = client.post(
        path=reverse("api:order-list"),
        data={"cart_id": cart_1_item.id, "region": local_limit.name}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert str(response.data[0]) == "['Global limit exceeded.']"

    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    with freeze_time(tomorrow):
        assert global_limit.limit_size == 3

        response = client.post(
            path=reverse("api:order-list"),
            data={"cart_id": cart_1_item.id, "region": local_limit.name}
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert datetime.date.today() == tomorrow


def test_create_order_first_day_local_limit_exceeded_second_day_renewed(
        db, user, client, shelf, global_limit, local_limit,
        cart_1_item
):
    global_limit.limit_size = 99
    global_limit.save()
    CartItemFactory(shelf=shelf, cart=cart_1_item)

    response = client.post(
        path=reverse("api:order-list"),
        data={"cart_id": cart_1_item.id, "region": local_limit.name}
    )

    assert response.status_code == status.HTTP_201_CREATED

    response = client.post(
        path=reverse("api:order-list"),
        data={"cart_id": cart_1_item.id, "region": local_limit.name}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert str(response.data[0]) == "['Region EU: closed or limit exceeded.']"

    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    with freeze_time(tomorrow):
        assert local_limit.limit_size == 3

        response = client.post(
            path=reverse("api:order-list"),
            data={"cart_id": cart_1_item.id, "region": local_limit.name}
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert datetime.date.today() == tomorrow
