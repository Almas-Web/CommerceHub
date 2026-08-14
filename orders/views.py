from django.db import transaction

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

from .models import Order, OrderItem
from .serializers import (
    AdminOrderUpdateSerializer,
    OrderSerializer,
    SellerOrderSerializer
)
from cart.models import Cart


@extend_schema(tags=['Orders'])
class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()

        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related('items__product')

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        shipping_address = request.data.get('shipping_address')

        if not shipping_address:
            return Response(
                {"detail": "Shipping address is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cart = Cart.objects.prefetch_related(
                'items__product'
            ).get(user=request.user)
        except Cart.DoesNotExist:
            return Response(
                {"detail": "Cart not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        cart_items = cart.items.all()

        if not cart_items.exists():
            return Response(
                {"detail": "Your cart is empty."},
                status=status.HTTP_400_BAD_REQUEST
            )

        total_amount = 0

        for cart_item in cart_items:
            product = cart_item.product

            if cart_item.quantity > product.stock:
                return Response(
                    {
                        "detail": (
                            f"Not enough stock for "
                            f"{product.name}."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            total_amount += product.price * cart_item.quantity

        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            total_amount=total_amount
        )

        for cart_item in cart_items:
            product = cart_item.product

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=cart_item.quantity,
                price=product.price
            )

            product.stock -= cart_item.quantity
            product.save(update_fields=['stock'])

        cart_items.delete()

        serializer = self.get_serializer(order)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


@extend_schema(tags=['Orders'])
class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()

        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related('items__product')


@extend_schema(tags=['Orders'])
class CancelOrderView(generics.GenericAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()

        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related('items__product')

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        order = self.get_object()

        if order.status != Order.Status.PENDING:
            return Response(
                {
                    "detail": (
                        "Only pending orders can be cancelled."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        for item in order.items.select_related('product'):
            product = item.product

            product.stock += item.quantity
            product.save(update_fields=['stock'])

        order.status = Order.Status.CANCELLED
        order.save(update_fields=['status', 'updated_at'])

        serializer = self.get_serializer(order)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


@extend_schema(tags=['Orders'])
class AdminOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()

        if self.request.user.role != 'ADMIN':
            return Order.objects.none()

        return Order.objects.all().prefetch_related(
            'items__product'
        ).select_related('user')


@extend_schema(tags=['Orders'])
class AdminOrderStatusUpdateView(generics.UpdateAPIView):
    serializer_class = AdminOrderUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    http_method_names = ['patch']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()

        if self.request.user.role != 'ADMIN':
            return Order.objects.none()

        return Order.objects.all().prefetch_related(
            'items__product'
        ).select_related('user')

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        order = self.get_object()
        old_status = order.status

        serializer = self.get_serializer(
            order,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data.get('status')

        if (
            new_status == Order.Status.CANCELLED
            and old_status != Order.Status.CANCELLED
        ):
            for item in order.items.select_related('product'):
                product = item.product
                product.stock += item.quantity

                product.save(
                    update_fields=['stock']
                )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


@extend_schema(tags=['Orders'])
class SellerOrderListView(generics.ListAPIView):
    serializer_class = SellerOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()

        if self.request.user.role != 'SELLER':
            return Order.objects.none()

        return Order.objects.filter(
            items__product__seller=self.request.user
        ).distinct().prefetch_related(
            'items__product'
        ).select_related('user')


@extend_schema(tags=['Orders'])
class SellerOrderStatusUpdateView(generics.UpdateAPIView):
    serializer_class = AdminOrderUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    http_method_names = ['patch']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()

        if self.request.user.role != 'SELLER':
            return Order.objects.none()

        return Order.objects.filter(
            items__product__seller=self.request.user
        ).distinct().prefetch_related(
            'items__product'
        ).select_related('user')

    def update(self, request, *args, **kwargs):
        order = self.get_object()

        serializer = self.get_serializer(
            order,
            data=request.data,
            partial=True
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )