from django.urls import path, include
from rest_framework import routers

from orders.views import OrderViewSet

router = routers.DefaultRouter()
router.register('order', OrderViewSet, basename="order")

urlpatterns = [
    path('api/', include((router.urls, 'api'), namespace='api')),
]
