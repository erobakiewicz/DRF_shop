from django.contrib import admin

from carts.models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem


@admin.register(Cart)
class CartItemAdmin(admin.ModelAdmin):
    inlines = [CartItemInline, ]
