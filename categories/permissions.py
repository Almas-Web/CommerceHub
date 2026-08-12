from rest_framework.permissions import BasePermission
from users.models import CustomUser
class IsAdmin(BasePermission):
    """
    Only Admin users can create, update and delete categories.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == CustomUser.Role.ADMIN