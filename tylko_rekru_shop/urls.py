from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions, authentication

schema_view = get_schema_view(
    openapi.Info(
        title="Shop API",
        default_version='v1',
        description="API documentation",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.IsAuthenticated,],
    authentication_classes=[authentication.BasicAuthentication,],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger/', login_required(
        schema_view.with_ui('swagger', cache_timeout=0),
        login_url='/admin/login/'), name='schema-swagger-ui'
         ),
    path('', include('shop.urls')),
]
