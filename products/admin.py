from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'category',
        'seller',
        'price',
        'stock',
        'is_active',
        'created_at',
    )

    list_filter = (
        'category',
        'seller',
        'is_active',
        'created_at',
    )

    search_fields = (
        'name',
        'description',
        'seller__username',
        'seller__email',
    )

    ordering = ('-created_at',)