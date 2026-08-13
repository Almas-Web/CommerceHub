from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from .models import Review
from .serializers import ReviewSerializer
from .permissions import IsCustomer

from orders.models import OrderItem, Order


class ReviewCreateView(generics.CreateAPIView):

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    permission_classes = [
        IsAuthenticated,
        IsCustomer,
    ]

    def perform_create(self, serializer):

        user = self.request.user
        product = serializer.validated_data["product"]

        # Check whether customer purchased the product
        purchased = OrderItem.objects.filter(
            order__user=user,
            product=product,
            order__status=Order.Status.DELIVERED
        ).exists()

        if not purchased:
            raise ValidationError(
                "You can only review products you have purchased "
                "and received."
            )

        # Prevent duplicate review
        if Review.objects.filter(
            product=product,
            user=user
        ).exists():

            raise ValidationError(
                "You have already reviewed this product."
            )

        serializer.save(user=user)

class ProductReviewListView(generics.ListAPIView):

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        product_id = self.kwargs["product_id"]

        return Review.objects.filter(
            product_id=product_id
        ).select_related("user", "product").order_by("-created_at")

class ReviewUpdateView(generics.UpdateAPIView):

    serializer_class = ReviewSerializer
    permission_classes = [
        IsAuthenticated,
        IsCustomer,
    ]

    def get_queryset(self):
        return Review.objects.filter(
            user=self.request.user
        )

class ReviewDeleteView(generics.DestroyAPIView):

    serializer_class = ReviewSerializer
    permission_classes = [
        IsAuthenticated,
        IsCustomer,
    ]

    def get_queryset(self):
        return Review.objects.filter(
            user=self.request.user
        )