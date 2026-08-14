from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema, inline_serializer

from products.models import Product
from .models import Cart, CartItem
from .serializers import CartSerializer


CartItemRequestSerializer = inline_serializer(
    name='CartItemRequest',
    fields={
        'product': serializers.IntegerField(),
        'quantity': serializers.IntegerField(
            required=False,
            default=1
        ),
    }
)

CartQuantityRequestSerializer = inline_serializer(
    name='CartQuantityRequest',
    fields={
        'quantity': serializers.IntegerField(),
    }
)


@extend_schema(tags=['Cart'])
class CartView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=CartSerializer
    )
    def get(self, request):
        cart, created = Cart.objects.get_or_create(
            user=request.user
        )

        serializer = CartSerializer(cart)

        return Response(serializer.data)

    @extend_schema(
        request=CartItemRequestSerializer,
        responses=CartSerializer
    )
    def post(self, request):
        product_id = request.data.get('product')
        quantity = request.data.get('quantity', 1)

        if not product_id:
            return Response(
                {'error': 'Product ID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return Response(
                {'error': 'Quantity must be a valid number.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantity < 1:
            return Response(
                {'error': 'Quantity must be at least 1.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if quantity > product.stock:
            return Response(
                {'error': 'Not enough stock available.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart, created = Cart.objects.get_or_create(
            user=request.user
        )

        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            product=product
        )

        if item_created:
            cart_item.quantity = quantity
        else:
            new_quantity = cart_item.quantity + quantity

            if new_quantity > product.stock:
                return Response(
                    {'error': 'Not enough stock available.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            cart_item.quantity = new_quantity

        cart_item.save()

        return Response(
            CartSerializer(cart).data,
            status=status.HTTP_201_CREATED
        )


@extend_schema(tags=['Cart'])
class CartItemView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=CartQuantityRequestSerializer,
        responses=CartSerializer
    )
    def patch(self, request, item_id):
        try:
            cart_item = CartItem.objects.get(
                id=item_id,
                cart__user=request.user
            )
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Cart item not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        quantity = request.data.get('quantity')

        if quantity is None:
            return Response(
                {'error': 'Quantity is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return Response(
                {'error': 'Quantity must be a valid number.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantity < 1:
            return Response(
                {'error': 'Quantity must be at least 1.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantity > cart_item.product.stock:
            return Response(
                {'error': 'Not enough stock available.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item.quantity = quantity
        cart_item.save()

        return Response(
            CartSerializer(cart_item.cart).data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
        responses=CartSerializer
    )
    def delete(self, request, item_id):
        try:
            cart_item = CartItem.objects.get(
                id=item_id,
                cart__user=request.user
            )
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Cart item not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        cart = cart_item.cart
        cart_item.delete()

        return Response(
            CartSerializer(cart).data,
            status=status.HTTP_200_OK
        )