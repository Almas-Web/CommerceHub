from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated

from .models import Category
from .serializers import CategorySerializer
from .permissions import IsAdmin

from drf_spectacular.utils import extend_schema


# Category List & Create

@extend_schema(
    tags=['Categories'],
    summary='List or create categories',
    description=(
        'Retrieve all product categories or create a new category. '
        'Category creation is restricted to administrators.'
    )
)
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]

        return [
            IsAuthenticated(),
            IsAdmin()
        ]


# Category Detail

@extend_schema(
    tags=['Categories'],
    summary='Retrieve, update or delete category',
    description=(
        'Retrieve a category publicly. '
        'Updating or deleting a category requires administrator permission.'
    )
)
class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]

        return [
            IsAuthenticated(),
            IsAdmin()
        ]