import pytest
from django.urls import reverse
from rest_framework import status

from utils.constants import CartStatuses


@pytest.mark.django_db
class CartViewSetTestCase:
    url = reverse("api:cart-list")

    def test_add_item_to_cart(self, client, shelf, region):
        data = {
            "region": region.id,
            "cart_items": [
                {
                    "shelf": shelf.id
                }
            ]
        }

        response = client.post(path=reverse("api:cart-list"), data=data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data.get("status") == CartStatuses.OPEN
        assert response.data.get("cart_items")[0].get("shelf") == shelf.id

    def test_cannot_add_non_existing_item_to_cart(self, client, region):
        data = {
            "region": region.id,
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
