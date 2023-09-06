import datetime

from django.urls import reverse
from freezegun import freeze_time
from rest_framework import status

from shop.models import Order
from shop.tests.factories import CartItemFactory


def test_add_item_to_cart(db, get_client, get_shelf, get_local_limit):
    data = {
        "region": get_local_limit.id,
        "cart_items": [
            {
                "shelf": get_shelf.id
            }
        ]
    }

    response = get_client.post(path=reverse("api:cart-list"), data=data, format="json")

    assert response.status_code == 201
    expected_shelf = get_shelf.id
    assert response.data.get("status") == 'OP'
    assert response.data.get("cart_items")[0].get("shelf") == expected_shelf


def test_cannot_add_non_existing_item_to_cart(db, get_client, get_local_limit):
    data = {
        "region": get_local_limit.id,
        "cart_items": [
            {
                "shelf": 12345
            }
        ]
    }

    response = get_client.post(path=reverse("api:cart-list"), data=data, format="json")

    assert response.status_code == 400
    assert response.data.get("cart_items")[0].get("shelf")[0] == 'Invalid pk "12345" - object does not exist.'


def test_cannot_add_item_to_cart_non_existing_region(db, get_client, get_shelf):
    data = {
        "region": 12345,
        "cart_items": [
            {
                "shelf": get_shelf.id
            }
        ]
    }

    response = get_client.post(path=reverse("api:cart-list"), data=data, format="json")

    assert response.status_code == 400
    assert response.data.get("region")[0] == 'Invalid pk "12345" - object does not exist.'


def test_create_order_from_cart(
        db, get_user, get_client, get_shelf, get_global_limit, get_local_limit, cart_1_item
):
    response = get_client.post(
        path=reverse("api:order-list"),
        data={"cart_id": cart_1_item.id, "region": get_local_limit.name}
    )

    assert response.status_code == status.HTTP_201_CREATED
    expected_order = Order.objects.get(user=get_user)
    assert response.data.get("order_id") == expected_order.id
    assert response.data.get("order_status") == "PD"
    assert expected_order.region.name == get_local_limit.name
    assert response.data.get("shelves")[0].get("item").get("name") == get_shelf.name
    cart_1_item.refresh_from_db()
    assert cart_1_item.status == "CL"


def test_cannot_create_order_from_non_existing_cart(db, get_client, get_local_limit):
    response = get_client.post(
        path=reverse("api:order-list"),
        data={"cart_id": 12345, "region": get_local_limit.name}
    )
    assert response.status_code == 400
    assert response.data.get("cart_id")[0] == "Cart does not belong to user or does not exist."


def test_cannot_create_order_from_non_existing_region(
        db, get_user, get_client, get_shelf, get_global_limit, get_local_limit, cart_1_item
):
    response = get_client.post(path=reverse("api:order-list"), data={"cart_id": cart_1_item.id, "region": "Mordor"})

    assert response.status_code == 400
    assert response.data.get("region")[0] == "Region does not exist."


def test_cannot_create_order_from_cart_global_limit_not_set(
        db, get_user, get_client, get_shelf, get_local_limit, cart_1_item
):
    response = get_client.post(
        path=reverse("api:order-list"),
        data={"cart_id": cart_1_item.id, "region": get_local_limit.name}
    )
    assert response.status_code == 400
    assert response.data[0] == 'Global limit not set.'


def test_cannot_create_order_from_cart_global_limit_1_local_limit_3(
        db, get_user, get_client, get_shelf, get_global_limit, get_local_limit, cart_1_item,
):
    get_global_limit.limit_size = 1
    get_global_limit.save(update_fields=['limit_size'])
    CartItemFactory(shelf=get_shelf, cart=cart_1_item)

    response = get_client.post(
        path=reverse("api:order-list"),
        data={"cart_id": cart_1_item.id, "region": get_local_limit.name}
    )

    assert response.status_code == 400
    assert str(response.data[0]) == "['Global limit exceeded.']"


def test_cannot_create_order_from_cart_local_limit_1_global_limit_3(
        db, get_user, get_client, get_shelf, get_global_limit, get_local_limit, cart_1_item
):
    CartItemFactory(shelf=get_shelf, cart=cart_1_item)

    get_local_limit.limit_size = 1
    get_local_limit.save(update_fields=['limit_size'])
    response = get_client.post(
        path=reverse("api:order-list"),
        data={"cart_id": cart_1_item.id, "region": get_local_limit.name}
    )

    assert response.status_code == 400
    assert str(response.data[0]) == "['Region EU: closed or limit exceeded.']"


def test_create_order_from_cart_first_region_exceed_different_region_allow(
        db, get_user, get_client, get_shelf, get_global_limit, get_local_limit, cart_1_item_different_region,
        cart_1_item
):
    CartItemFactory(shelf=get_shelf, cart=cart_1_item)

    get_local_limit.limit_size = 1
    get_local_limit.save(update_fields=['limit_size'])
    response = get_client.post(
        path=reverse("api:order-list"),
        data={"cart_id": cart_1_item.id, "region": get_local_limit.name}
    )

    assert response.status_code == 400
    assert str(response.data[0]) == "['Region EU: closed or limit exceeded.']"

    response = get_client.post(
        path=reverse("api:order-list"),
        data={"cart_id": cart_1_item_different_region.id, "region": cart_1_item_different_region.region.name}
    )
    assert response.status_code == 201


def test_create_order_first_day_global_limit_exceeded_second_day_renewed(
        db, get_user, get_client, get_shelf, get_global_limit, get_local_limit,
        cart_1_item
):
    CartItemFactory(shelf=get_shelf, cart=cart_1_item)

    response = get_client.post(
        path=reverse("api:order-list"),
        data={"cart_id": cart_1_item.id, "region": get_local_limit.name}
    )

    assert response.status_code == 201

    response = get_client.post(
        path=reverse("api:order-list"),
        data={"cart_id": cart_1_item.id, "region": get_local_limit.name}
    )

    assert response.status_code == 400
    assert str(response.data[0]) == "['Global limit exceeded.']"

    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    with freeze_time(tomorrow):
        assert get_global_limit.limit_size == 3

        response = get_client.post(
            path=reverse("api:order-list"),
            data={"cart_id": cart_1_item.id, "region": get_local_limit.name}
        )

        assert response.status_code == 201
        assert datetime.date.today() == tomorrow


def test_create_order_first_day_local_limit_exceeded_second_day_renewed(
        db, get_user, get_client, get_shelf, get_global_limit, get_local_limit,
        cart_1_item
):
    get_global_limit.limit_size = 99
    get_global_limit.save()
    CartItemFactory(shelf=get_shelf, cart=cart_1_item)

    response = get_client.post(
        path=reverse("api:order-list"),
        data={"cart_id": cart_1_item.id, "region": get_local_limit.name}
    )

    assert response.status_code == 201

    response = get_client.post(
        path=reverse("api:order-list"),
        data={"cart_id": cart_1_item.id, "region": get_local_limit.name}
    )

    assert response.status_code == 400
    assert str(response.data[0]) == "['Region EU: closed or limit exceeded.']"

    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    with freeze_time(tomorrow):
        assert get_local_limit.limit_size == 3

        response = get_client.post(
            path=reverse("api:order-list"),
            data={"cart_id": cart_1_item.id, "region": get_local_limit.name}
        )

        assert response.status_code == 201
        assert datetime.date.today() == tomorrow
