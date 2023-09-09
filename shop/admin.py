from django.contrib import admin

from shop.models import Shelf, Region, GlobalProductLimit, Order, OrderItem, Cart, CartItem


@admin.register(GlobalProductLimit)
class GlobalProductLimitAdmin(admin.ModelAdmin):
    pass


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ["name", "limit_size", "closed_access", "unlimited_access"]
    pass


@admin.register(Shelf)
class ShelfAdmin(admin.ModelAdmin):
    pass


class OrderItemInline(admin.TabularInline):
    model = OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ["created_at"]
    list_display = ["user", "region", "status", "created_at"]
    inlines = [OrderItemInline, ]


class CartItemInline(admin.TabularInline):
    model = CartItem


@admin.register(Cart)
class CartItemAdmin(admin.ModelAdmin):
    inlines = [CartItemInline, ]
