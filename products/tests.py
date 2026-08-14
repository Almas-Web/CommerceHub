import pytest

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from categories.models import Category
from users.models import CustomUser

from .models import Product


pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user():
    return CustomUser.objects.create_user(
        username="adminuser",
        email="admin@example.com",
        password="AdminPassword123",
        role=CustomUser.Role.ADMIN,
        is_verified=True,
    )


@pytest.fixture
def seller_user():
    return CustomUser.objects.create_user(
        username="selleruser",
        email="seller@example.com",
        password="SellerPassword123",
        role=CustomUser.Role.SELLER,
        is_verified=True,
    )


@pytest.fixture
def another_seller():
    return CustomUser.objects.create_user(
        username="anotherseller",
        email="another@example.com",
        password="SellerPassword123",
        role=CustomUser.Role.SELLER,
        is_verified=True,
    )


@pytest.fixture
def customer_user():
    return CustomUser.objects.create_user(
        username="customeruser",
        email="customer@example.com",
        password="CustomerPassword123",
        role=CustomUser.Role.CUSTOMER,
        is_verified=True,
    )


@pytest.fixture
def category():
    return Category.objects.create(
        name="Electronics",
        description="Electronic products",
    )


@pytest.fixture
def product(category, seller_user):
    return Product.objects.create(
        name="iPhone 15",
        description="Apple iPhone 15",
        price="89999.00",
        stock=10,
        category=category,
        seller=seller_user,
        is_active=True,
    )


# Product List

def test_product_list_public(
    api_client,
    product,
):
    response = api_client.get(
        reverse("product-list-create")
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["count"] == 1

    result = response.data["results"][0]

    assert result["name"] == "iPhone 15"
    assert result["description"] == "Apple iPhone 15"
    assert result["price"] == "89999.00"
    assert result["stock"] == 10
    assert result["category"] == product.category.id
    assert result["seller"] == product.seller.username
    assert result["is_active"] is True


def test_product_list_without_products(api_client):
    response = api_client.get(
        reverse("product-list-create")
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []


# Product Detail

def test_product_detail_public(
    api_client,
    product,
):
    response = api_client.get(
        reverse(
            "product-detail",
            kwargs={
                "pk": product.id
            },
        )
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["id"] == product.id
    assert response.data["name"] == "iPhone 15"
    assert response.data["price"] == "89999.00"
    assert response.data["seller"] == product.seller.username


def test_product_detail_not_found(api_client):
    response = api_client.get(
        reverse(
            "product-detail",
            kwargs={
                "pk": 99999
            },
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


# Product Create

def test_seller_can_create_product(
    api_client,
    seller_user,
    category,
):
    api_client.force_authenticate(
        user=seller_user
    )

    response = api_client.post(
        reverse("product-list-create"),
        {
            "name": "Samsung Galaxy S24",
            "description": "Premium Samsung smartphone",
            "price": "89999.00",
            "stock": 20,
            "category": category.id,
            "is_active": True,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    assert response.data["name"] == "Samsung Galaxy S24"
    assert response.data["seller"] == seller_user.username

    created_product = Product.objects.get(
        name="Samsung Galaxy S24"
    )

    assert created_product.seller == seller_user
    assert created_product.category == category
    assert created_product.stock == 20


def test_admin_can_create_product(
    api_client,
    admin_user,
    category,
):
    api_client.force_authenticate(
        user=admin_user
    )

    response = api_client.post(
        reverse("product-list-create"),
        {
            "name": "Admin Product",
            "description": "Product created by admin",
            "price": "5000.00",
            "stock": 5,
            "category": category.id,
            "is_active": True,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    product = Product.objects.get(
        name="Admin Product"
    )

    assert product.seller == admin_user


def test_customer_cannot_create_product(
    api_client,
    customer_user,
    category,
):
    api_client.force_authenticate(
        user=customer_user
    )

    response = api_client.post(
        reverse("product-list-create"),
        {
            "name": "Customer Product",
            "description": "Should not be created",
            "price": "5000.00",
            "stock": 5,
            "category": category.id,
            "is_active": True,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_unauthenticated_user_cannot_create_product(
    api_client,
    category,
):
    response = api_client.post(
        reverse("product-list-create"),
        {
            "name": "Unauthorized Product",
            "description": "Should not be created",
            "price": "5000.00",
            "stock": 5,
            "category": category.id,
            "is_active": True,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Product Ownership

def test_seller_can_update_own_product(
    api_client,
    seller_user,
    product,
):
    api_client.force_authenticate(
        user=seller_user
    )

    response = api_client.patch(
        reverse(
            "product-detail",
            kwargs={
                "pk": product.id
            },
        ),
        {
            "name": "Updated iPhone 15",
            "price": "85000.00",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    product.refresh_from_db()

    assert product.name == "Updated iPhone 15"
    assert str(product.price) == "85000.00"


def test_seller_can_delete_own_product(
    api_client,
    seller_user,
    product,
):
    api_client.force_authenticate(
        user=seller_user
    )

    response = api_client.delete(
        reverse(
            "product-detail",
            kwargs={
                "pk": product.id
            },
        )
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not Product.objects.filter(
        id=product.id
    ).exists()


def test_seller_cannot_update_other_seller_product(
    api_client,
    another_seller,
    product,
):
    api_client.force_authenticate(
        user=another_seller
    )

    response = api_client.patch(
        reverse(
            "product-detail",
            kwargs={
                "pk": product.id
            },
        ),
        {
            "name": "Hacked Product",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    product.refresh_from_db()

    assert product.name == "iPhone 15"


def test_seller_cannot_delete_other_seller_product(
    api_client,
    another_seller,
    product,
):
    api_client.force_authenticate(
        user=another_seller
    )

    response = api_client.delete(
        reverse(
            "product-detail",
            kwargs={
                "pk": product.id
            },
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    assert Product.objects.filter(
        id=product.id
    ).exists()


# Admin Product Management

def test_admin_can_update_any_product(
    api_client,
    admin_user,
    product,
):
    api_client.force_authenticate(
        user=admin_user
    )

    response = api_client.patch(
        reverse(
            "product-detail",
            kwargs={
                "pk": product.id
            },
        ),
        {
            "name": "Admin Updated Product",
            "price": "75000.00",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    product.refresh_from_db()

    assert product.name == "Admin Updated Product"
    assert str(product.price) == "75000.00"


def test_admin_can_delete_any_product(
    api_client,
    admin_user,
    product,
):
    api_client.force_authenticate(
        user=admin_user
    )

    response = api_client.delete(
        reverse(
            "product-detail",
            kwargs={
                "pk": product.id
            },
        )
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not Product.objects.filter(
        id=product.id
    ).exists()


# Product Filtering

def test_filter_product_by_category(
    api_client,
    product,
):
    response = api_client.get(
        reverse("product-list-create"),
        {
            "category": product.category.id
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == product.id


def test_filter_product_by_min_price(
    api_client,
    product,
):
    response = api_client.get(
        reverse("product-list-create"),
        {
            "price__gte": "80000"
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1


def test_filter_product_by_max_price(
    api_client,
    product,
):
    response = api_client.get(
        reverse("product-list-create"),
        {
            "price__lte": "50000"
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0


def test_filter_active_products(
    api_client,
    category,
    seller_user,
):
    Product.objects.create(
        name="Active Product",
        description="Active product",
        price="1000.00",
        stock=10,
        category=category,
        seller=seller_user,
        is_active=True,
    )

    Product.objects.create(
        name="Inactive Product",
        description="Inactive product",
        price="2000.00",
        stock=10,
        category=category,
        seller=seller_user,
        is_active=False,
    )

    response = api_client.get(
        reverse("product-list-create"),
        {
            "is_active": "true"
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["name"] == "Active Product"


# Product Search

def test_search_product_by_name(
    api_client,
    product,
):
    response = api_client.get(
        reverse("product-list-create"),
        {
            "search": "iPhone"
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["name"] == "iPhone 15"


def test_search_product_by_description(
    api_client,
    product,
):
    response = api_client.get(
        reverse("product-list-create"),
        {
            "search": "Apple"
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1


def test_search_product_not_found(
    api_client,
    product,
):
    response = api_client.get(
        reverse("product-list-create"),
        {
            "search": "Laptop"
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0


# Product Ordering

def test_order_products_by_price(
    api_client,
    category,
    seller_user,
):
    Product.objects.create(
        name="Cheap Product",
        description="Cheap product",
        price="1000.00",
        stock=10,
        category=category,
        seller=seller_user,
    )

    Product.objects.create(
        name="Expensive Product",
        description="Expensive product",
        price="5000.00",
        stock=10,
        category=category,
        seller=seller_user,
    )

    response = api_client.get(
        reverse("product-list-create"),
        {
            "ordering": "price"
        },
    )

    assert response.status_code == status.HTTP_200_OK

    results = response.data["results"]

    assert results[0]["name"] == "Cheap Product"
    assert results[1]["name"] == "Expensive Product"


# Product Pagination

def test_product_pagination(
    api_client,
    category,
    seller_user,
):
    for index in range(12):
        Product.objects.create(
            name=f"Product {index}",
            description=f"Product description {index}",
            price=f"{1000 + index}.00",
            stock=10,
            category=category,
            seller=seller_user,
        )

    response = api_client.get(
        reverse("product-list-create")
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["count"] == 12
    assert len(response.data["results"]) == 10

    assert response.data["next"] is not None


def test_product_custom_page_size(
    api_client,
    category,
    seller_user,
):
    for index in range(12):
        Product.objects.create(
            name=f"Product {index}",
            description=f"Product description {index}",
            price=f"{1000 + index}.00",
            stock=10,
            category=category,
            seller=seller_user,
        )

    response = api_client.get(
        reverse("product-list-create"),
        {
            "page_size": 5
        },
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["count"] == 12
    assert len(response.data["results"]) == 5