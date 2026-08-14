import pytest

from decimal import Decimal

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from users.models import CustomUser
from categories.models import Category
from products.models import Product

from .models import Cart, CartItem


pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


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
def another_customer():
    return CustomUser.objects.create_user(
        username="anothercustomer",
        email="another@example.com",
        password="CustomerPassword123",
        role=CustomUser.Role.CUSTOMER,
        is_verified=True,
    )


@pytest.fixture
def category():
    return Category.objects.create(
        name="Cart Electronics",
        description="Products for cart testing",
    )


@pytest.fixture
def product(category, customer_user):
    return Product.objects.create(
        name="Cart Product",
        description="Product for cart testing",
        price=Decimal("1000.00"),
        stock=10,
        category=category,
        seller=customer_user,
        is_active=True,
    )


@pytest.fixture
def second_product(category, customer_user):
    return Product.objects.create(
        name="Second Cart Product",
        description="Second product for cart testing",
        price=Decimal("500.00"),
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
def cart(customer_user):
    return Cart.objects.create(
        user=customer_user
    )


@pytest.fixture
def cart_item(cart, product):
    return CartItem.objects.create(
        cart=cart,
        product=product,
        quantity=2,
    )


# Authentication

def test_unauthenticated_user_cannot_view_cart(
    api_client,
):
    response = api_client.get(
        reverse("cart")
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_unauthenticated_user_cannot_add_to_cart(
    api_client,
    product,
):
    response = api_client.post(
        reverse("cart"),
        {
            "product": product.id,
            "quantity": 1,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# View Cart

def test_authenticated_user_can_view_empty_cart(
    authenticated_client,
    customer_user,
):
    response = authenticated_client.get(
        reverse("cart")
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["user"] == customer_user.id
    assert response.data["items"] == []
    assert str(response.data["cart_total"]) == "0.00"

    assert Cart.objects.filter(
        user=customer_user
    ).exists()


def test_view_cart_with_items(
    authenticated_client,
    customer_user,
    cart_item,
):
    response = authenticated_client.get(
        reverse("cart")
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["user"] == customer_user.id
    assert len(response.data["items"]) == 1

    item = response.data["items"][0]

    assert item["product"] == cart_item.product.id
    assert item["product_name"] == "Cart Product"
    assert item["price"] == "1000.00"
    assert item["quantity"] == 2
    assert str(item["subtotal"]) == "2000.00"

    assert str(response.data["cart_total"]) == "2000.00"


# Add Product

def test_authenticated_user_can_add_product_to_cart(
    authenticated_client,
    customer_user,
    product,
):
    response = authenticated_client.post(
        reverse("cart"),
        {
            "product": product.id,
            "quantity": 2,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    cart = Cart.objects.get(
        user=customer_user
    )

    cart_item = CartItem.objects.get(
        cart=cart,
        product=product,
    )

    assert cart_item.quantity == 2

    assert str(response.data["cart_total"]) == "2000.00"


def test_add_product_without_product_id(
    authenticated_client,
):
    response = authenticated_client.post(
        reverse("cart"),
        {
            "quantity": 1,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.data["error"] == "Product ID is required."


def test_add_non_existing_product(
    authenticated_client,
):
    response = authenticated_client.post(
        reverse("cart"),
        {
            "product": 99999,
            "quantity": 1,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.data["error"] == "Product not found."


# Quantity Validation

def test_add_product_with_invalid_quantity(
    authenticated_client,
    product,
):
    response = authenticated_client.post(
        reverse("cart"),
        {
            "product": product.id,
            "quantity": "invalid",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.data["error"] == (
        "Quantity must be a valid number."
    )


def test_add_product_with_zero_quantity(
    authenticated_client,
    product,
):
    response = authenticated_client.post(
        reverse("cart"),
        {
            "product": product.id,
            "quantity": 0,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.data["error"] == (
        "Quantity must be at least 1."
    )


def test_add_product_with_negative_quantity(
    authenticated_client,
    product,
):
    response = authenticated_client.post(
        reverse("cart"),
        {
            "product": product.id,
            "quantity": -1,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.data["error"] == (
        "Quantity must be at least 1."
    )


def test_add_product_quantity_greater_than_stock(
    authenticated_client,
    product,
):
    response = authenticated_client.post(
        reverse("cart"),
        {
            "product": product.id,
            "quantity": 11,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.data["error"] == (
        "Not enough stock available."
    )


# Same Product

def test_adding_same_product_increases_quantity(
    authenticated_client,
    product,
):
    first_response = authenticated_client.post(
        reverse("cart"),
        {
            "product": product.id,
            "quantity": 2,
        },
        format="json",
    )

    assert first_response.status_code == status.HTTP_201_CREATED

    second_response = authenticated_client.post(
        reverse("cart"),
        {
            "product": product.id,
            "quantity": 3,
        },
        format="json",
    )

    assert second_response.status_code == status.HTTP_201_CREATED

    cart = Cart.objects.get(
        user=product.seller
    )

    cart_item = CartItem.objects.get(
        cart=cart,
        product=product,
    )

    assert cart_item.quantity == 5


def test_same_product_cannot_exceed_stock(
    authenticated_client,
    product,
):
    authenticated_client.post(
        reverse("cart"),
        {
            "product": product.id,
            "quantity": 7,
        },
        format="json",
    )

    response = authenticated_client.post(
        reverse("cart"),
        {
            "product": product.id,
            "quantity": 4,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.data["error"] == (
        "Not enough stock available."
    )


# Cart Total

def test_cart_total_with_multiple_products(
    authenticated_client,
    customer_user,
    product,
    second_product,
):
    authenticated_client.post(
        reverse("cart"),
        {
            "product": product.id,
            "quantity": 2,
        },
        format="json",
    )

    authenticated_client.post(
        reverse("cart"),
        {
            "product": second_product.id,
            "quantity": 3,
        },
        format="json",
    )

    response = authenticated_client.get(
        reverse("cart")
    )

    assert response.status_code == status.HTTP_200_OK

    assert len(response.data["items"]) == 2

    assert str(response.data["cart_total"]) == "3500.00"


# Update Cart Item

def test_user_can_update_cart_item_quantity(
    authenticated_client,
    cart_item,
):
    response = authenticated_client.patch(
        reverse(
            "cart-item",
            kwargs={
                "item_id": cart_item.id
            },
        ),
        {
            "quantity": 5,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    cart_item.refresh_from_db()

    assert cart_item.quantity == 5
    assert str(response.data["cart_total"]) == "5000.00"


def test_update_cart_item_without_quantity(
    authenticated_client,
    cart_item,
):
    response = authenticated_client.patch(
        reverse(
            "cart-item",
            kwargs={
                "item_id": cart_item.id
            },
        ),
        {},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.data["error"] == (
        "Quantity is required."
    )


def test_update_cart_item_with_invalid_quantity(
    authenticated_client,
    cart_item,
):
    response = authenticated_client.patch(
        reverse(
            "cart-item",
            kwargs={
                "item_id": cart_item.id
            },
        ),
        {
            "quantity": "invalid",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.data["error"] == (
        "Quantity must be a valid number."
    )


def test_update_cart_item_with_zero_quantity(
    authenticated_client,
    cart_item,
):
    response = authenticated_client.patch(
        reverse(
            "cart-item",
            kwargs={
                "item_id": cart_item.id
            },
        ),
        {
            "quantity": 0,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.data["error"] == (
        "Quantity must be at least 1."
    )


def test_update_cart_item_with_negative_quantity(
    authenticated_client,
    cart_item,
):
    response = authenticated_client.patch(
        reverse(
            "cart-item",
            kwargs={
                "item_id": cart_item.id
            },
        ),
        {
            "quantity": -2,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.data["error"] == (
        "Quantity must be at least 1."
    )


def test_update_cart_item_greater_than_stock(
    authenticated_client,
    cart_item,
):
    response = authenticated_client.patch(
        reverse(
            "cart-item",
            kwargs={
                "item_id": cart_item.id
            },
        ),
        {
            "quantity": 11,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.data["error"] == (
        "Not enough stock available."
    )


# Remove Cart Item

def test_user_can_remove_cart_item(
    authenticated_client,
    cart_item,
):
    cart_id = cart_item.cart.id
    item_id = cart_item.id

    response = authenticated_client.delete(
        reverse(
            "cart-item",
            kwargs={
                "item_id": item_id
            },
        )
    )

    assert response.status_code == status.HTTP_200_OK

    assert not CartItem.objects.filter(
        id=item_id
    ).exists()

    assert Cart.objects.filter(
        id=cart_id
    ).exists()

    assert response.data["items"] == []
    assert str(response.data["cart_total"]) == "0.00"


def test_remove_non_existing_cart_item(
    authenticated_client,
):
    response = authenticated_client.delete(
        reverse(
            "cart-item",
            kwargs={
                "item_id": 99999
            },
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.data["error"] == (
        "Cart item not found."
    )


# User Isolation

def test_user_cannot_update_another_users_cart_item(
    api_client,
    another_customer,
    cart_item,
):
    api_client.force_authenticate(
        user=another_customer
    )

    response = api_client.patch(
        reverse(
            "cart-item",
            kwargs={
                "item_id": cart_item.id
            },
        ),
        {
            "quantity": 5,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.data["error"] == (
        "Cart item not found."
    )


def test_user_cannot_delete_another_users_cart_item(
    api_client,
    another_customer,
    cart_item,
):
    api_client.force_authenticate(
        user=another_customer
    )

    response = api_client.delete(
        reverse(
            "cart-item",
            kwargs={
                "item_id": cart_item.id
            },
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.data["error"] == (
        "Cart item not found."
    )

    assert CartItem.objects.filter(
        id=cart_item.id
    ).exists()


def test_user_cannot_see_another_users_cart(
    api_client,
    customer_user,
    another_customer,
):
    Cart.objects.create(
        user=another_customer
    )

    api_client.force_authenticate(
        user=customer_user
    )

    response = api_client.get(
        reverse("cart")
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["user"] == customer_user.id

    assert response.data["items"] == []