from django.urls import path, include
from rest_framework import routers

from carts.views import CartViewSet

router = routers.DefaultRouter()
router.register('cart', CartViewSet, basename="cart")

urlpatterns = [
    path('api/', include((router.urls, 'api'), namespace='api')),
]
