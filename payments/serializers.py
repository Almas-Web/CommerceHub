from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):

    order_total = serializers.DecimalField(
        source='order.total_amount',
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Payment
        fields = [
            'id',
            'order',
            'user',
            'transaction_id',
            'amount',
            'order_total',
            'method',
            'status',
            'created_at',
        ]

        read_only_fields = [
            'id',
            'user',
            'amount',
            'order_total',
            'status',
            'created_at',
        ]