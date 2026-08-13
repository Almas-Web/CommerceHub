from django.urls import path

from .views import (
    PaymentCreateView,
    PaymentStatusUpdateView,
)

urlpatterns = [
    path(
        '',
        PaymentCreateView.as_view(),
        name='payment-create'
    ),

    path(
        '<int:pk>/status/',
        PaymentStatusUpdateView.as_view(),
        name='payment-status-update'
    ),
]