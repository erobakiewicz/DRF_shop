from django import forms
from django.contrib import admin

from orders.models import Order, OrderItem


# Register your models here.
class OrderItemFormSet(forms.BaseInlineFormSet):
    pass


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    formset = OrderItemFormSet


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ["created_at"]
    list_display = ["user", "region", "status", "created_at"]
    inlines = [OrderItemInline, ]
