import pytest

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from users.models import CustomUser
from categories.models import Category
from products.models import Product

from .models import Wishlist


pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def customer_user():
    return CustomUser.objects.create_user(
        username="wishlistcustomer",
        email="wishlistcustomer@example.com",
        password="CustomerPassword123",
        role=CustomUser.Role.CUSTOMER,
        is_verified=True,
    )


@pytest.fixture
def another_customer():
    return CustomUser.objects.create_user(
        username="anotherwishlistcustomer",
        email="anotherwishlist@example.com",
        password="CustomerPassword123",
        role=CustomUser.Role.CUSTOMER,
        is_verified=True,
    )


@pytest.fixture
def category():
    return Category.objects.create(
        name="Wishlist Electronics",
        description="Products for wishlist testing",
    )


@pytest.fixture
def product(category, customer_user):
    return Product.objects.create(
        name="Wishlist Product",
        description="Product for wishlist testing",
        price="50000.00",
        stock=10,
        category=category,
        seller=customer_user,
        is_active=True,
    )


@pytest.fixture
def second_product(category, customer_user):
    return Product.objects.create(
        name="Second Wishlist Product",
        description="Second product for wishlist testing",
        price="75000.00",
        stock=15,
        category=category,
        seller=customer_user,
        is_active=True,
    )


@pytest.fixture
def third_product(category, customer_user):
    return Product.objects.create(
        name="Third Wishlist Product",
        description="Third product for wishlist testing",
        price="25000.00",
        stock=20,
        category=category,
        seller=customer_user,
        is_active=True,
    )


@pytest.fixture
def authenticated_client(api_client, customer_user):
    api_client.force_authenticate(
        user=customer_user
    )
    return api_client


@pytest.fixture
def wishlist(customer_user):
    return Wishlist.objects.create(
        user=customer_user
    )


# Authentication

def test_unauthenticated_user_cannot_view_wishlist(
    api_client,
):
    response = api_client.get(
        reverse("wishlist")
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_unauthenticated_user_cannot_add_to_wishlist(
    api_client,
    product,
):
    response = api_client.post(
        reverse(
            "wishlist-add",
            kwargs={
                "product_id": product.id
            },
        )
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_unauthenticated_user_cannot_remove_from_wishlist(
    api_client,
    product,
):
    response = api_client.delete(
        reverse(
            "wishlist-remove",
            kwargs={
                "product_id": product.id
            },
        )
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# View Wishlist

def test_authenticated_user_can_view_empty_wishlist(
    authenticated_client,
    customer_user,
):
    response = authenticated_client.get(
        reverse("wishlist")
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["user"] == customer_user.id
    assert response.data["products"] == []

    assert Wishlist.objects.filter(
        user=customer_user
    ).exists()


def test_view_wishlist_with_product(
    authenticated_client,
    customer_user,
    product,
):
    wishlist = Wishlist.objects.create(
        user=customer_user
    )

    wishlist.products.add(product)

    response = authenticated_client.get(
        reverse("wishlist")
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["user"] == customer_user.id

    assert product.id in response.data["products"]


# Add Product

def test_user_can_add_product_to_wishlist(
    authenticated_client,
    customer_user,
    product,
):
    response = authenticated_client.post(
        reverse(
            "wishlist-add",
            kwargs={
                "product_id": product.id
            },
        )
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["detail"] == (
        "Product added to wishlist."
    )

    wishlist = Wishlist.objects.get(
        user=customer_user
    )

    assert wishlist.products.filter(
        id=product.id
    ).exists()


def test_add_non_existing_product_to_wishlist(
    authenticated_client,
):
    response = authenticated_client.post(
        reverse(
            "wishlist-add",
            kwargs={
                "product_id": 99999
            },
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.data["detail"] == (
        "Product not found."
    )


def test_adding_same_product_twice_does_not_duplicate(
    authenticated_client,
    customer_user,
    product,
):
    first_response = authenticated_client.post(
        reverse(
            "wishlist-add",
            kwargs={
                "product_id": product.id
            },
        )
    )

    second_response = authenticated_client.post(
        reverse(
            "wishlist-add",
            kwargs={
                "product_id": product.id
            },
        )
    )

    assert first_response.status_code == status.HTTP_200_OK
    assert second_response.status_code == status.HTTP_200_OK

    wishlist = Wishlist.objects.get(
        user=customer_user
    )

    assert wishlist.products.filter(
        id=product.id
    ).count() == 1


# Multiple Products

def test_user_can_add_multiple_products_to_wishlist(
    authenticated_client,
    customer_user,
    product,
    second_product,
    third_product,
):
    authenticated_client.post(
        reverse(
            "wishlist-add",
            kwargs={
                "product_id": product.id
            },
        )
    )

    authenticated_client.post(
        reverse(
            "wishlist-add",
            kwargs={
                "product_id": second_product.id
            },
        )
    )

    authenticated_client.post(
        reverse(
            "wishlist-add",
            kwargs={
                "product_id": third_product.id
            },
        )
    )

    wishlist = Wishlist.objects.get(
        user=customer_user
    )

    assert wishlist.products.count() == 3

    assert wishlist.products.filter(
        id=product.id
    ).exists()

    assert wishlist.products.filter(
        id=second_product.id
    ).exists()

    assert wishlist.products.filter(
        id=third_product.id
    ).exists()


# Remove Product

def test_user_can_remove_product_from_wishlist(
    authenticated_client,
    customer_user,
    product,
):
    wishlist = Wishlist.objects.create(
        user=customer_user
    )

    wishlist.products.add(product)

    response = authenticated_client.delete(
        reverse(
            "wishlist-remove",
            kwargs={
                "product_id": product.id
            },
        )
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["detail"] == (
        "Product removed from wishlist."
    )

    wishlist.refresh_from_db()

    assert not wishlist.products.filter(
        id=product.id
    ).exists()


def test_remove_product_not_in_wishlist(
    authenticated_client,
    customer_user,
    product,
):
    response = authenticated_client.delete(
        reverse(
            "wishlist-remove",
            kwargs={
                "product_id": product.id
            },
        )
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["detail"] == (
        "Product removed from wishlist."
    )


def test_remove_non_existing_product(
    authenticated_client,
):
    response = authenticated_client.delete(
        reverse(
            "wishlist-remove",
            kwargs={
                "product_id": 99999
            },
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.data["detail"] == (
        "Product not found."
    )


# Update Wishlist

def test_user_can_update_wishlist(
    authenticated_client,
    customer_user,
    product,
    second_product,
):
    wishlist = Wishlist.objects.create(
        user=customer_user
    )

    wishlist.products.add(product)

    response = authenticated_client.put(
        reverse("wishlist"),
        {
            "products": [
                product.id,
                second_product.id,
            ]
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    wishlist.refresh_from_db()

    assert wishlist.products.count() == 2

    assert wishlist.products.filter(
        id=product.id
    ).exists()

    assert wishlist.products.filter(
        id=second_product.id
    ).exists()


def test_user_can_replace_wishlist_products(
    authenticated_client,
    customer_user,
    product,
    second_product,
    third_product,
):
    wishlist = Wishlist.objects.create(
        user=customer_user
    )

    wishlist.products.add(
        product,
        second_product,
    )

    response = authenticated_client.put(
        reverse("wishlist"),
        {
            "products": [
                third_product.id
            ]
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    wishlist.refresh_from_db()

    assert wishlist.products.count() == 1

    assert wishlist.products.filter(
        id=third_product.id
    ).exists()

    assert not wishlist.products.filter(
        id=product.id
    ).exists()

    assert not wishlist.products.filter(
        id=second_product.id
    ).exists()


def test_user_can_clear_wishlist(
    authenticated_client,
    customer_user,
    product,
    second_product,
):
    wishlist = Wishlist.objects.create(
        user=customer_user
    )

    wishlist.products.add(
        product,
        second_product,
    )

    response = authenticated_client.put(
        reverse("wishlist"),
        {
            "products": []
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    wishlist.refresh_from_db()

    assert wishlist.products.count() == 0


# User Isolation

def test_user_cannot_see_another_users_wishlist(
    api_client,
    customer_user,
    another_customer,
    product,
):
    another_wishlist = Wishlist.objects.create(
        user=another_customer
    )

    another_wishlist.products.add(product)

    api_client.force_authenticate(
        user=customer_user
    )

    response = api_client.get(
        reverse("wishlist")
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["user"] == customer_user.id
    assert response.data["products"] == []


def test_user_cannot_modify_another_users_wishlist(
    api_client,
    customer_user,
    another_customer,
    product,
    second_product,
):
    another_wishlist = Wishlist.objects.create(
        user=another_customer
    )

    another_wishlist.products.add(product)

    api_client.force_authenticate(
        user=customer_user
    )

    response = api_client.put(
        reverse("wishlist"),
        {
            "products": [
                second_product.id
            ]
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    another_wishlist.refresh_from_db()

    assert another_wishlist.products.count() == 1

    assert another_wishlist.products.filter(
        id=product.id
    ).exists()

    assert not another_wishlist.products.filter(
        id=second_product.id
    ).exists()


def test_user_can_only_remove_from_own_wishlist(
    api_client,
    customer_user,
    another_customer,
    product,
):
    another_wishlist = Wishlist.objects.create(
        user=another_customer
    )

    another_wishlist.products.add(product)

    api_client.force_authenticate(
        user=customer_user
    )

    response = api_client.delete(
        reverse(
            "wishlist-remove",
            kwargs={
                "product_id": product.id
            },
        )
    )

    assert response.status_code == status.HTTP_200_OK

    another_wishlist.refresh_from_db()

    assert another_wishlist.products.filter(
        id=product.id
    ).exists()