from django.urls import path
from .views import (
    WishlistView,
    AddToWishlistView,
    RemoveFromWishlistView,
)

urlpatterns = [
    path('', WishlistView.as_view(), name='wishlist'),
    path(
        'add/<int:product_id>/',
        AddToWishlistView.as_view(),
        name='wishlist-add'
    ),
    path(
        'remove/<int:product_id>/',
        RemoveFromWishlistView.as_view(),
        name='wishlist-remove'
    ),
]