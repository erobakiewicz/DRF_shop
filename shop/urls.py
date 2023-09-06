from django.urls import path, include
from rest_framework import routers

from shop.views import CartViewSet, OrderViewSet

router = routers.DefaultRouter()
router.register('cart', CartViewSet, basename="cart")
router.register('order', OrderViewSet, basename="order")

urlpatterns = [
    path('api/', include((router.urls, 'api'), namespace='api')),
]
