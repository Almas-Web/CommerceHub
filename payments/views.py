from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import Payment
from .serializers import PaymentSerializer
from orders.models import Order


class PaymentCreateView(generics.CreateAPIView):

    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def create(self, request, *args, **kwargs):

        order_id = request.data.get('order')
        method = request.data.get('method')
        transaction_id = request.data.get('transaction_id')

        if not order_id:
            return Response(
                {
                    "detail": "Order is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            order = Order.objects.get(
                id=order_id,
                user=request.user
            )
        except Order.DoesNotExist:
            return Response(
                {
                    "detail": "Order not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if order.status == Order.Status.CANCELLED:
            return Response(
                {
                    "detail": "Cancelled orders cannot be paid."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if hasattr(order, 'payment'):
            return Response(
                {
                    "detail": "Payment already exists for this order."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not method:
            return Response(
                {
                    "detail": "Payment method is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not transaction_id:
            return Response(
                {
                    "detail": "Transaction ID is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        payment = Payment.objects.create(
            order=order,
            user=request.user,
            transaction_id=transaction_id,
            amount=order.total_amount,
            method=method,
            status=Payment.Status.PENDING
        )

        serializer = self.get_serializer(payment)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )
class PaymentStatusUpdateView(generics.UpdateAPIView):

    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'ADMIN':
            return Payment.objects.all()

        return Payment.objects.filter(
            user=self.request.user
        )

    @transaction.atomic
    def update(self, request, *args, **kwargs):

        payment = self.get_object()

        new_status = request.data.get('status')

        allowed_transitions = {
            Payment.Status.PENDING: [
                Payment.Status.SUCCESS,
                Payment.Status.FAILED,
            ],
            Payment.Status.SUCCESS: [
                Payment.Status.REFUNDED,
            ],
            Payment.Status.FAILED: [],
            Payment.Status.REFUNDED: [],
        }

        if new_status not in Payment.Status.values:
            return Response(
                {
                    "detail": "Invalid payment status."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if new_status not in allowed_transitions[
            payment.status
        ]:
            return Response(
                {
                    "detail": (
                        f"Cannot change payment status "
                        f"from {payment.status} "
                        f"to {new_status}."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        payment.status = new_status
        payment.save(update_fields=['status'])

        serializer = self.get_serializer(payment)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )