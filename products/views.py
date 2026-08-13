from rest_framework import generics, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product
from .serializers import ProductSerializer
from .permissions import IsSellerOrAdmin


class ProductPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = {
        'category': ['exact'],
        'price': ['gte', 'lte'],
        'is_active': ['exact'],
    }

    search_fields = [
        'name',
        'description',
    ]

    ordering_fields = [
        'price',
        'name',
        'created_at',
    ]

    ordering = ['-created_at']

    pagination_class = ProductPagination

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]

        return [
            permissions.IsAuthenticated(),
            IsSellerOrAdmin()
        ]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]

        return [
            permissions.IsAuthenticated(),
            IsSellerOrAdmin()
        ]