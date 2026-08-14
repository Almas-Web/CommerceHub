from decimal import Decimal

from rest_framework import serializers

from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name",
        read_only=True
    )

    price = serializers.DecimalField(
        source="product.price",
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "product_name",
            "price",
            "quantity",
            "subtotal",
        ]

    def get_subtotal(self, obj: CartItem) -> Decimal:
        return obj.product.price * obj.quantity


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(
        many=True,
        read_only=True
    )

    cart_total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            "id",
            "user",
            "items",
            "cart_total",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "user",
            "created_at",
            "updated_at",
        ]

    def get_cart_total(self, obj: Cart) -> Decimal:
        return sum(
            (
                item.product.price * item.quantity
                for item in obj.items.all()
            ),
            Decimal("0.00")
        )