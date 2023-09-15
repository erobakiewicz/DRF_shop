import datetime

import pytest
from django.urls import reverse
from freezegun import freeze_time
from rest_framework import status

from orders.models import Order
from utils.constants import OrderStatuses, CartStatuses, ErrorMessages
from utils.factories import CartItemFactory


@pytest.mark.django_db
class OrderViewSetTestCase:
    url = reverse("api:order-list")

    def test_create_order(
            self, user, client, product, global_limit, region, cart_1_item
    ):
        response = client.post(
            path=self.url,
            data={"cart_id": cart_1_item.id}
        )

        assert response.status_code == status.HTTP_201_CREATED
        expected_order = Order.objects.get(user=user)
        assert response.data.get("order_id") == expected_order.id

    def test_create_order_belongs_to_authenticated_user(
            self, user, client, product, global_limit, region, cart_1_item
    ):
        response = client.post(
            path=self.url,
            data={"cart_id": cart_1_item.id}
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert Order.objects.get(id=response.data.get("order_id")).user == user

    def test_created_order_have_expected_data(
            self, user, client, product, global_limit, region, cart_1_item
    ):
        response = client.post(
            path=self.url,
            data={"cart_id": cart_1_item.id}
        )
        expected_order = Order.objects.get(id=response.data.get("order_id"))

        assert response.status_code == status.HTTP_201_CREATED

        assert response.data.get("order_status") == OrderStatuses.PENDING
        assert expected_order.region.name == region.name
        assert response.data.get("shelves")[0].get("item").get("name") == product.name
        cart_1_item.refresh_from_db()
        assert cart_1_item.status == CartStatuses.CLOSED

    def test_create_order_unlimited_access_region(
            self, user, client, product, global_limit, region, cart_1_item
    ):
        region.unlimited_access = True
        region.limit_size = 0
        region.save(update_fields=['unlimited_access', 'limit_size'])

        response = client.post(
            path=self.url,
            data={"cart_id": cart_1_item.id}
        )

        assert response.status_code == status.HTTP_201_CREATED
        expected_order = Order.objects.get(user=user)
        assert response.data.get("order_id") == expected_order.id
        assert response.data.get("order_status") == OrderStatuses.PENDING
        assert expected_order.region.name == region.name
        assert response.data.get("shelves")[0].get("item").get("name") == product.name
        cart_1_item.refresh_from_db()
        assert cart_1_item.status == CartStatuses.CLOSED

    def test_cannot_create_order_from_non_existing_cart(self, client, region):
        response = client.post(
            path=self.url,
            data={"cart_id": 12345, "region": region.name}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get("cart_id")[0] == ErrorMessages.CART_USER_MISMATCH

    def test_cannot_create_order_from_cart_global_limit_not_set(
            self, user, client, product, region, cart_1_item
    ):
        response = client.post(
            path=self.url,
            data={"cart_id": cart_1_item.id}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data[0] == ErrorMessages.GLOBAL_LIMIT_NOT_SET

    def test_cannot_create_order_closed_access(
            self, user, client, product, global_limit, region, cart_1_item
    ):
        region.closed_access = True
        region.save(update_fields=['closed_access'])

        response = client.post(
            path=self.url,
            data={"cart_id": cart_1_item.id}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data[0] == ErrorMessages.REGION_LIMIT_EXCEEDED.format(region.name)

    def test_cannot_create_order_when_global_limit_exceeded_but_local_not(
            self, user, client, product, global_limit, region, cart_1_item,
    ):
        global_limit.limit_size = 1
        global_limit.save(update_fields=['limit_size'])
        CartItemFactory.create_batch(2, cart=cart_1_item)

        response = client.post(
            path=self.url,
            data={"cart_id": cart_1_item.id}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert str(response.data[0]) == "Global limit exceeded."

    def test_cannot_create_order_when_local_limit_exceeded_but_global_not(
            self, user, client, product, global_limit, region, cart_1_item
    ):
        CartItemFactory.create_batch(2, cart=cart_1_item)

        region.limit_size = 1
        region.save(update_fields=['limit_size'])

        response = client.post(
            path=self.url,
            data={"cart_id": cart_1_item.id}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert str(response.data[0]) == "Region EU: closed or limit exceeded."

    def test_create_order_from_cart_first_region_exceed_different_region_allow(
            self, user, client, product, global_limit, region, cart_1_item_second_region,
            cart_1_item
    ):
        CartItemFactory(product=product, cart=cart_1_item)

        region.limit_size = 1
        region.save(update_fields=['limit_size'])
        response = client.post(
            path=self.url,
            data={"cart_id": cart_1_item.id}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert str(response.data[0]) == "Region EU: closed or limit exceeded."

        response = client.post(
            path=self.url,
            data={
                "cart_id": cart_1_item_second_region.id,
                "region": cart_1_item_second_region.region.name
            }
        )

        assert response.status_code == status.HTTP_201_CREATED

    def test_create_order_first_day_global_limit_exceeded_second_day_renewed(
            self, user, client, product, global_limit, region,
            cart_1_item
    ):
        CartItemFactory(product=product, cart=cart_1_item)

        response = client.post(
            path=self.url,
            data={"cart_id": cart_1_item.id}
        )

        assert response.status_code == status.HTTP_201_CREATED

        response = client.post(
            path=self.url,
            data={"cart_id": cart_1_item.id}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert str(response.data[0]) == "Global limit exceeded."

        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        with freeze_time(tomorrow):
            assert global_limit.limit_size == 3

            response = client.post(
                path=self.url,
                data={"cart_id": cart_1_item.id}
            )

            assert response.status_code == status.HTTP_201_CREATED
            assert datetime.date.today() == tomorrow

    def test_create_order_first_day_region_exceeded_second_day_renewed(
            self, user, client, product, global_limit, region,
            cart_1_item
    ):
        global_limit.limit_size = 99
        global_limit.save()
        CartItemFactory(product=product, cart=cart_1_item)

        response = client.post(
            path=self.url,
            data={"cart_id": cart_1_item.id}
        )

        assert response.status_code == status.HTTP_201_CREATED

        response = client.post(
            path=self.url,
            data={"cart_id": cart_1_item.id}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert str(response.data[0]) == "Region EU: closed or limit exceeded."

        tomorrow = datetime.date.today() + datetime.timedelta(days=1)

        with freeze_time(tomorrow):
            assert region.limit_size == 3

            response = client.post(
                path=self.url,
                data={"cart_id": cart_1_item.id}
            )

            assert response.status_code == status.HTTP_201_CREATED
            assert datetime.date.today() == tomorrow
