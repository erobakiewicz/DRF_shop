from django.contrib import admin

from shop.models import Product, Region, GlobalProductLimit


@admin.register(GlobalProductLimit)
class GlobalProductLimitAdmin(admin.ModelAdmin):
    pass


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ["name", "limit_size", "closed_access", "unlimited_access"]
    pass


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass
