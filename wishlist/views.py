from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import Wishlist
from .serializers import WishlistSerializer
from products.models import Product


class WishlistView(generics.RetrieveUpdateAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        wishlist, created = Wishlist.objects.get_or_create(
            user=self.request.user
        )
        return wishlist

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


class AddToWishlistView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, product_id):
        wishlist, created = Wishlist.objects.get_or_create(
            user=request.user
        )

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        wishlist.products.add(product)

        return Response(
            {"detail": "Product added to wishlist."},
            status=status.HTTP_200_OK
        )


class RemoveFromWishlistView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, product_id):
        wishlist, created = Wishlist.objects.get_or_create(
            user=request.user
        )

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        wishlist.products.remove(product)

        return Response(
            {"detail": "Product removed from wishlist."},
            status=status.HTTP_200_OK
        )