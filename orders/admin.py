from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        'product',
        'quantity',
        'price',
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'status',
        'total_amount',
        'shipping_address',
        'created_at',
        'updated_at',
    )

    list_filter = (
        'status',
        'created_at',
    )

    search_fields = (
        'user__username',
        'user__email',
        'shipping_address',
    )

    readonly_fields = (
        'user',
        'total_amount',
        'created_at',
        'updated_at',
    )

    inlines = [
        OrderItemInline,
    ]