from django.urls import path
from .views import (
    AdminOrderListView,
    AdminOrderStatusUpdateView,
    OrderListCreateView,
    OrderDetailView,
    CancelOrderView,
    SellerOrderListView,
    SellerOrderStatusUpdateView,
)
urlpatterns = [
    path('', OrderListCreateView.as_view(), name='order-list-create'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path(
        '<int:pk>/cancel/',
        CancelOrderView.as_view(),
        name='order-cancel'
    ),
    path(
    'admin/',
    AdminOrderListView.as_view(),
    name='admin-order-list'
),

    path(
    'admin/<int:pk>/status/',
    AdminOrderStatusUpdateView.as_view(),
    name='admin-order-status-update'
),
    path(
    'seller/',
    SellerOrderListView.as_view(),
    name='seller-order-list'
),

    path(
    'seller/<int:pk>/status/',
    SellerOrderStatusUpdateView.as_view(),
    name='seller-order-status-update'
),
]