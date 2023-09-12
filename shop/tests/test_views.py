import datetime

import pytest
from django.urls import reverse
from freezegun import freeze_time
from rest_framework import status

from shop.constants import CartStatuses, OrderStatuses, ErrorMessages
from shop.models import Order
from shop.tests.factories import CartItemFactory, RegionFactory


@pytest.mark.django_db
class CartViewSetTestCase:
    url = reverse("api:cart-list")

    def test_add_item_to_cart(self, client, shelf, local_limit):
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

    def test_cannot_add_non_existing_item_to_cart(self, client, local_limit):
        data = {
            "region": local_limit.id,
            "cart_items": [
                {
                    "shelf": 12345
                }
            ]
        }

        response = client.post(path=self.url, data=data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get("cart_items")[0].get("shelf")[0] == 'Invalid pk "12345" - object does not exist.'

    def test_cannot_add_item_to_cart_non_existing_region(self, client, shelf):
        data = {
            "region": 12345,
            "cart_items": [
                {
                    "shelf": shelf.id
                }
            ]
        }

        response = client.post(path=self.url, data=data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get("region")[0] == 'Invalid pk "12345" - object does not exist.'


@pytest.mark.django_db
class OrderViewSetTestCase:
    url = reverse("api:order-list")

    def test_create_order(
            self, user, client, shelf, global_limit, local_limit, cart_1_item
    ):
        response = client.post(
            path=self.url,
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

    def test_create_order_unlimited_access_region(
            self, user, client, shelf, global_limit, local_limit, cart_1_item
    ):
        local_limit.unlimited_access = True
        local_limit.limit_size = 0
        local_limit.save(update_fields=['unlimited_access', 'limit_size'])

        response = client.post(
            path=self.url,
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

    def test_cannot_create_order_from_non_existing_cart(self, client, local_limit):
        response = client.post(
            path=self.url,
            data={"cart_id": 12345, "region": local_limit.name}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get("cart_id")[0] == ErrorMessages.CART_USER_MISMATCH

    def test_cannot_create_order_from_mismatch_region(
            self, user, client, shelf, global_limit, local_limit, cart_1_item
    ):
        other_region = RegionFactory(name="Gondor")
        response = client.post(
            path=self.url,
            data={"cart_id": cart_1_item.id, "region": other_region.name}

        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get("non_field_errors")[0] == ErrorMessages.ORDER_CART_REGIONS_MISMATCH

    def test_cannot_create_order_from_non_existing_region(
            self, user, client, shelf, global_limit, local_limit, cart_1_item
    ):
        response = client.post(
            path=self.url,
            data={"cart_id": cart_1_item.id,
                  "region": "Mordor"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get("region")[0] == ErrorMessages.REGION_DOES_NOT_EXIST

    def test_cannot_create_order_from_cart_global_limit_not_set(
            self, user, client, shelf, local_limit, cart_1_item
    ):
        response = client.post(
            path=self.url,
            data={"cart_id": cart_1_item.id, "region": local_limit.name}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data[0] == ErrorMessages.GLOBAL_LIMIT_NOT_SET

    def test_cannot_create_order_closed_access(
            self, user, client, shelf, global_limit, local_limit, cart_1_item
    ):
        local_limit.closed_access = True
        local_limit.save(update_fields=['closed_access'])

        response = client.post(
            path=self.url,
            data={"cart_id": cart_1_item.id, "region": local_limit.name}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data[0] == ErrorMessages.REGION_LIMIT_EXCEEDED.format(local_limit.name)

    def test_cannot_create_order_from_cart_global_limit_1_local_limit_3(
            self, user, client, shelf, global_limit, local_limit, cart_1_item,
    ):
        global_limit.limit_size = 1
        global_limit.save(update_fields=['limit_size'])
        CartItemFactory.create_batch(2, cart=cart_1_item)

        response = client.post(
            path=self.url,
            data={"cart_id": cart_1_item.id, "region": local_limit.name}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert str(response.data[0]) == "Global limit exceeded."

    def test_cannot_create_order_from_cart_local_limit_1_global_limit_3(
            self, user, client, shelf, global_limit, local_limit, cart_1_item
    ):
        CartItemFactory.create_batch(2, cart=cart_1_item)

        local_limit.limit_size = 1
        local_limit.save(update_fields=['limit_size'])

        response = client.post(
            path=self.url,
            data={"cart_id": cart_1_item.id, "region": local_limit.name}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert str(response.data[0]) == "Region EU: closed or limit exceeded."

    def test_create_order_from_cart_first_region_exceed_different_region_allow(
            self, user, client, shelf, global_limit, local_limit, cart_1_item_different_region,
            cart_1_item
    ):
        CartItemFactory(shelf=shelf, cart=cart_1_item)

        local_limit.limit_size = 1
        local_limit.save(update_fields=['limit_size'])
        response = client.post(
            path=self.url,
            data={"cart_id": cart_1_item.id, "region": local_limit.name}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert str(response.data[0]) == "Region EU: closed or limit exceeded."

        response = client.post(
            path=self.url,
            data={
                "cart_id": cart_1_item_different_region.id,
                "region": cart_1_item_different_region.region.name
            }
        )

        assert response.status_code == status.HTTP_201_CREATED

    def test_create_order_first_day_global_limit_exceeded_second_day_renewed(
            self, user, client, shelf, global_limit, local_limit,
            cart_1_item
    ):
        CartItemFactory(shelf=shelf, cart=cart_1_item)

        response = client.post(
            path=self.url,
            data={"cart_id": cart_1_item.id, "region": local_limit.name}
        )

        assert response.status_code == status.HTTP_201_CREATED

        response = client.post(
            path=self.url,
            data={"cart_id": cart_1_item.id, "region": local_limit.name}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert str(response.data[0]) == "Global limit exceeded."

        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        with freeze_time(tomorrow):
            assert global_limit.limit_size == 3

            response = client.post(
                path=self.url,
                data={"cart_id": cart_1_item.id, "region": local_limit.name}
            )

            assert response.status_code == status.HTTP_201_CREATED
            assert datetime.date.today() == tomorrow

    def test_create_order_first_day_local_limit_exceeded_second_day_renewed(
            self, user, client, shelf, global_limit, local_limit,
            cart_1_item
    ):
        global_limit.limit_size = 99
        global_limit.save()
        CartItemFactory(shelf=shelf, cart=cart_1_item)

        response = client.post(
            path=self.url,
            data={"cart_id": cart_1_item.id, "region": local_limit.name}
        )

        assert response.status_code == status.HTTP_201_CREATED

        response = client.post(
            path=self.url,
            data={"cart_id": cart_1_item.id, "region": local_limit.name}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert str(response.data[0]) == "Region EU: closed or limit exceeded."

        tomorrow = datetime.date.today() + datetime.timedelta(days=1)

        with freeze_time(tomorrow):
            assert local_limit.limit_size == 3

            response = client.post(
                path=self.url,
                data={"cart_id": cart_1_item.id, "region": local_limit.name}
            )

            assert response.status_code == status.HTTP_201_CREATED
            assert datetime.date.today() == tomorrow
