from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'product',
        'user',
        'rating',
        'comment',
        'created_at',
        'updated_at',
    )

    list_filter = (
        'rating',
        'created_at',
    )

    search_fields = (
        'product__name',
        'user__username',
        'user__email',
        'comment',
    )

    readonly_fields = (
        'user',
        'product',
        'created_at',
        'updated_at',
    )

    ordering = (
        '-created_at',
    )