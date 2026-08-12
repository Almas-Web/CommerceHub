from rest_framework.permissions import BasePermission

from users.models import CustomUser


class IsSellerOrAdmin(BasePermission):
    """
    Seller can create and manage their own products.
    Admin can manage all products.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.role in [
            CustomUser.Role.SELLER,
            CustomUser.Role.ADMIN,
        ]

    def has_object_permission(self, request, view, obj):
        if request.user.role == CustomUser.Role.ADMIN:
            return True

        return obj.seller == request.user