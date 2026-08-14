import pytest

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from .models import Category
from users.models import CustomUser


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


# Category List

def test_category_list_public(api_client, category):
    response = api_client.get(
        reverse("category-list-create")
    )

    assert response.status_code == status.HTTP_200_OK

    assert len(response.data) == 1
    assert response.data[0]["name"] == "Electronics"
    assert response.data[0]["description"] == "Electronic products"


def test_category_list_without_categories(api_client):
    response = api_client.get(
        reverse("category-list-create")
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data == []


# Category Detail

def test_category_detail_public(
    api_client,
    category,
):
    response = api_client.get(
        reverse(
            "category-detail",
            kwargs={
                "pk": category.id
            },
        )
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["id"] == category.id
    assert response.data["name"] == "Electronics"
    assert response.data["description"] == "Electronic products"


def test_category_detail_not_found(api_client):
    response = api_client.get(
        reverse(
            "category-detail",
            kwargs={
                "pk": 99999
            },
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


# Category Create

def test_admin_can_create_category(
    api_client,
    admin_user,
):
    api_client.force_authenticate(
        user=admin_user
    )

    response = api_client.post(
        reverse("category-list-create"),
        {
            "name": "Clothing",
            "description": "Clothing products",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    assert response.data["name"] == "Clothing"
    assert response.data["description"] == "Clothing products"

    assert Category.objects.filter(
        name="Clothing"
    ).exists()


def test_unauthenticated_user_cannot_create_category(
    api_client,
):
    response = api_client.post(
        reverse("category-list-create"),
        {
            "name": "Books",
            "description": "Book products",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_customer_cannot_create_category(
    api_client,
    customer_user,
):
    api_client.force_authenticate(
        user=customer_user
    )

    response = api_client.post(
        reverse("category-list-create"),
        {
            "name": "Books",
            "description": "Book products",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_seller_cannot_create_category(
    api_client,
    seller_user,
):
    api_client.force_authenticate(
        user=seller_user
    )

    response = api_client.post(
        reverse("category-list-create"),
        {
            "name": "Books",
            "description": "Book products",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_duplicate_category_name_not_allowed(
    api_client,
    admin_user,
    category,
):
    api_client.force_authenticate(
        user=admin_user
    )

    response = api_client.post(
        reverse("category-list-create"),
        {
            "name": "Electronics",
            "description": "Another description",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert Category.objects.filter(
        name="Electronics"
    ).count() == 1


def test_category_description_optional(
    api_client,
    admin_user,
):
    api_client.force_authenticate(
        user=admin_user
    )

    response = api_client.post(
        reverse("category-list-create"),
        {
            "name": "Sports",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    category = Category.objects.get(
        name="Sports"
    )

    assert category.description == ""


# Category Update

def test_admin_can_update_category(
    api_client,
    admin_user,
    category,
):
    api_client.force_authenticate(
        user=admin_user
    )

    response = api_client.patch(
        reverse(
            "category-detail",
            kwargs={
                "pk": category.id
            },
        ),
        {
            "name": "Updated Electronics",
            "description": "Updated description",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    category.refresh_from_db()

    assert category.name == "Updated Electronics"
    assert category.description == "Updated description"


def test_customer_cannot_update_category(
    api_client,
    customer_user,
    category,
):
    api_client.force_authenticate(
        user=customer_user
    )

    response = api_client.patch(
        reverse(
            "category-detail",
            kwargs={
                "pk": category.id
            },
        ),
        {
            "name": "Updated Electronics",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    category.refresh_from_db()

    assert category.name == "Electronics"


def test_seller_cannot_update_category(
    api_client,
    seller_user,
    category,
):
    api_client.force_authenticate(
        user=seller_user
    )

    response = api_client.patch(
        reverse(
            "category-detail",
            kwargs={
                "pk": category.id
            },
        ),
        {
            "name": "Updated Electronics",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    category.refresh_from_db()

    assert category.name == "Electronics"


def test_unauthenticated_user_cannot_update_category(
    api_client,
    category,
):
    response = api_client.patch(
        reverse(
            "category-detail",
            kwargs={
                "pk": category.id
            },
        ),
        {
            "name": "Updated Electronics",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Category Delete

def test_admin_can_delete_category(
    api_client,
    admin_user,
    category,
):
    api_client.force_authenticate(
        user=admin_user
    )

    response = api_client.delete(
        reverse(
            "category-detail",
            kwargs={
                "pk": category.id
            },
        )
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not Category.objects.filter(
        id=category.id
    ).exists()


def test_customer_cannot_delete_category(
    api_client,
    customer_user,
    category,
):
    api_client.force_authenticate(
        user=customer_user
    )

    response = api_client.delete(
        reverse(
            "category-detail",
            kwargs={
                "pk": category.id
            },
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    assert Category.objects.filter(
        id=category.id
    ).exists()


def test_seller_cannot_delete_category(
    api_client,
    seller_user,
    category,
):
    api_client.force_authenticate(
        user=seller_user
    )

    response = api_client.delete(
        reverse(
            "category-detail",
            kwargs={
                "pk": category.id
            },
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    assert Category.objects.filter(
        id=category.id
    ).exists()


def test_unauthenticated_user_cannot_delete_category(
    api_client,
    category,
):
    response = api_client.delete(
        reverse(
            "category-detail",
            kwargs={
                "pk": category.id
            },
        )
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    assert Category.objects.filter(
        id=category.id
    ).exists()


# Category Timestamp

def test_category_created_at_is_set(category):
    assert category.created_at is not None