from django.urls import path, include
from rest_framework import routers

from orders.views import OrderViewSet
from carts.views import CartViewSet

router = routers.DefaultRouter()
router.register('cart', CartViewSet, basename="cart")
router.register('order', OrderViewSet, basename="order")

urlpatterns = [
    path('api/', include((router.urls, 'api'), namespace='api')),
]
