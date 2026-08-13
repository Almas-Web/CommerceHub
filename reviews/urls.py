from django.urls import path

from .views import (
    ReviewCreateView,
    ProductReviewListView,
    ReviewDeleteView,
    ReviewUpdateView,
)


urlpatterns = [
    path(
        "create/",
        ReviewCreateView.as_view(),
        name="review-create"
    ),

    path(
        "product/<int:product_id>/",
        ProductReviewListView.as_view(),
        name="product-review-list"
    ),

    path(
        "<int:pk>/update/",
        ReviewUpdateView.as_view(),
        name="review-update"
    ),
    path(
    "<int:pk>/delete/",
    ReviewDeleteView.as_view(),
    name="review-delete"
),
]