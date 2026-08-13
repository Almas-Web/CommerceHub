from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):

    product_name = serializers.CharField(
        source='product.name',
        read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product',
            'product_name',
            'quantity',
            'price',
        ]
        read_only_fields = [
            'id',
            'product_name',
            'price',
        ]


class OrderSerializer(serializers.ModelSerializer):

    items = OrderItemSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'status',
            'total_amount',
            'shipping_address',
            'items',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'status',
            'total_amount',
            'items',
            'created_at',
            'updated_at',
        ]

class AdminOrderUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'status',
            'total_amount',
            'shipping_address',
            'items',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'total_amount',
            'shipping_address',
            'items',
            'created_at',
            'updated_at',
        ]

    def validate_status(self, value):
        order = self.instance

        allowed_transitions = {
            Order.Status.PENDING: [
                Order.Status.CONFIRMED,
                Order.Status.CANCELLED,
            ],
            Order.Status.CONFIRMED: [
                Order.Status.PROCESSING,
                Order.Status.CANCELLED,
            ],
            Order.Status.PROCESSING: [
                Order.Status.SHIPPED,
            ],
            Order.Status.SHIPPED: [
                Order.Status.DELIVERED,
            ],
            Order.Status.DELIVERED: [],
            Order.Status.CANCELLED: [],
        }

        if order and value != order.status:
            allowed = allowed_transitions.get(order.status, [])

            if value not in allowed:
                raise serializers.ValidationError(
                    f"Cannot change order status from "
                    f"{order.status} to {value}."
                )

        return value
class SellerOrderSerializer(serializers.ModelSerializer):

    items = OrderItemSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'status',
            'total_amount',
            'shipping_address',
            'items',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'status',
            'total_amount',
            'shipping_address',
            'items',
            'created_at',
            'updated_at',
        ]