from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'order',
        'user',
        'transaction_id',
        'amount',
        'method',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'method',
        'created_at',
    )

    search_fields = (
        'transaction_id',
        'user__username',
        'user__email',
        'order__id',
    )

    readonly_fields = (
        'user',
        'order',
        'transaction_id',
        'amount',
        'created_at',
    )