import pytest
from decimal import Decimal

from rest_framework.test import APIClient

from users.models import CustomUser
from products.models import Product
from categories.models import Category
from cart.models import Cart, CartItem
from .models import Order, OrderItem


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def customer(db):
    return CustomUser.objects.create_user(
        username="customer",
        email="customer@example.com",
        password="TestPass123!",
        role=CustomUser.Role.CUSTOMER,
        is_verified=True,
    )


@pytest.fixture
def customer_two(db):
    return CustomUser.objects.create_user(
        username="customer2",
        email="customer2@example.com",
        password="TestPass123!",
        role=CustomUser.Role.CUSTOMER,
        is_verified=True,
    )


@pytest.fixture
def seller(db):
    return CustomUser.objects.create_user(
        username="seller",
        email="seller@example.com",
        password="TestPass123!",
        role=CustomUser.Role.SELLER,
        is_verified=True,
    )


@pytest.fixture
def seller_two(db):
    return CustomUser.objects.create_user(
        username="seller2",
        email="seller2@example.com",
        password="TestPass123!",
        role=CustomUser.Role.SELLER,
        is_verified=True,
    )


@pytest.fixture
def admin(db):
    return CustomUser.objects.create_user(
        username="admin",
        email="admin@example.com",
        password="TestPass123!",
        role=CustomUser.Role.ADMIN,
        is_verified=True,
    )


@pytest.fixture
def category(db):
    return Category.objects.create(
        name="Electronics",
        description="Electronic products",
    )


@pytest.fixture
def product(db, seller, category):
    return Product.objects.create(
        name="iPhone 15",
        description="Apple iPhone 15",
        price=Decimal("100000.00"),
        stock=10,
        category=category,
        seller=seller,
        is_active=True,
    )


@pytest.fixture
def second_product(db, seller, category):
    return Product.objects.create(
        name="Samsung Galaxy S24",
        description="Samsung smartphone",
        price=Decimal("80000.00"),
        stock=20,
        category=category,
        seller=seller,
        is_active=True,
    )


@pytest.fixture
def customer_cart(customer, product):
    cart = Cart.objects.create(user=customer)

    CartItem.objects.create(
        cart=cart,
        product=product,
        quantity=2,
    )

    return cart


@pytest.fixture
def authenticated_customer(api_client, customer):
    api_client.force_authenticate(user=customer)
    return api_client


@pytest.fixture
def authenticated_seller(api_client, seller):
    api_client.force_authenticate(user=seller)
    return api_client


@pytest.fixture
def authenticated_admin(api_client, admin):
    api_client.force_authenticate(user=admin)
    return api_client


def test_unauthenticated_user_cannot_create_order(
    api_client,
    product,
):
    response = api_client.post(
        "/api/orders/",
        {
            "shipping_address": "Barishal, Bangladesh",
        },
        format="json",
    )

    assert response.status_code == 401


def test_authenticated_user_cannot_create_order_without_shipping_address(
    authenticated_customer,
    customer,
    product,
):
    cart = Cart.objects.create(user=customer)

    CartItem.objects.create(
        cart=cart,
        product=product,
        quantity=1,
    )

    response = authenticated_customer.post(
        "/api/orders/",
        {},
        format="json",
    )

    assert response.status_code == 400
    assert response.data["detail"] == "Shipping address is required."


def test_authenticated_user_cannot_create_order_without_cart(
    authenticated_customer,
):
    response = authenticated_customer.post(
        "/api/orders/",
        {
            "shipping_address": "Barishal, Bangladesh",
        },
        format="json",
    )

    assert response.status_code == 404
    assert response.data["detail"] == "Cart not found."


def test_authenticated_user_cannot_create_order_with_empty_cart(
    authenticated_customer,
    customer,
):
    Cart.objects.create(user=customer)

    response = authenticated_customer.post(
        "/api/orders/",
        {
            "shipping_address": "Barishal, Bangladesh",
        },
        format="json",
    )

    assert response.status_code == 400
    assert response.data["detail"] == "Your cart is empty."


def test_user_can_create_order_from_cart(
    authenticated_customer,
    customer,
    product,
):
    cart = Cart.objects.create(user=customer)

    CartItem.objects.create(
        cart=cart,
        product=product,
        quantity=2,
    )

    original_stock = product.stock

    response = authenticated_customer.post(
        "/api/orders/",
        {
            "shipping_address": "Barishal, Bangladesh",
        },
        format="json",
    )

    assert response.status_code == 201

    order = Order.objects.get(
        id=response.data["id"]
    )

    assert order.user == customer
    assert order.status == Order.Status.PENDING
    assert order.total_amount == Decimal("200000.00")
    assert order.shipping_address == "Barishal, Bangladesh"

    assert order.items.count() == 1

    item = order.items.first()

    assert item.product == product
    assert item.quantity == 2
    assert item.price == Decimal("100000.00")

    product.refresh_from_db()

    assert product.stock == original_stock - 2

    assert not CartItem.objects.filter(
        cart=cart
    ).exists()


def test_order_total_with_multiple_products(
    authenticated_customer,
    customer,
    product,
    second_product,
):
    cart = Cart.objects.create(user=customer)

    CartItem.objects.create(
        cart=cart,
        product=product,
        quantity=2,
    )

    CartItem.objects.create(
        cart=cart,
        product=second_product,
        quantity=3,
    )

    response = authenticated_customer.post(
        "/api/orders/",
        {
            "shipping_address": "Dhaka, Bangladesh",
        },
        format="json",
    )

    assert response.status_code == 201

    order = Order.objects.get(
        id=response.data["id"]
    )

    expected_total = (
        Decimal("100000.00") * 2
        + Decimal("80000.00") * 3
    )

    assert order.total_amount == expected_total
    assert order.items.count() == 2


def test_user_cannot_create_order_when_stock_is_insufficient(
    authenticated_customer,
    customer,
    product,
):
    cart = Cart.objects.create(user=customer)

    CartItem.objects.create(
        cart=cart,
        product=product,
        quantity=product.stock + 1,
    )

    response = authenticated_customer.post(
        "/api/orders/",
        {
            "shipping_address": "Barishal, Bangladesh",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "Not enough stock" in response.data["detail"]

    assert not Order.objects.filter(
        user=customer
    ).exists()


def test_user_can_view_order_history(
    authenticated_customer,
    customer,
    product,
):
    order = Order.objects.create(
        user=customer,
        shipping_address="Barishal, Bangladesh",
        total_amount=Decimal("100000.00"),
    )

    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1,
        price=product.price,
    )

    response = authenticated_customer.get(
        "/api/orders/"
    )

    assert response.status_code == 200

    assert len(response.data) == 1
    assert response.data[0]["id"] == order.id


def test_user_can_view_order_detail(
    authenticated_customer,
    customer,
    product,
):
    order = Order.objects.create(
        user=customer,
        shipping_address="Barishal, Bangladesh",
        total_amount=product.price,
    )

    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1,
        price=product.price,
    )

    response = authenticated_customer.get(
        f"/api/orders/{order.id}/"
    )

    assert response.status_code == 200
    assert response.data["id"] == order.id
    assert response.data["user"] == customer.id
    assert len(response.data["items"]) == 1


def test_user_cannot_view_another_users_order(
    authenticated_customer,
    customer_two,
    product,
):
    order = Order.objects.create(
        user=customer_two,
        shipping_address="Dhaka, Bangladesh",
        total_amount=product.price,
    )

    response = authenticated_customer.get(
        f"/api/orders/{order.id}/"
    )

    assert response.status_code == 404


def test_user_can_cancel_pending_order(
    authenticated_customer,
    customer,
    product,
):
    order = Order.objects.create(
        user=customer,
        shipping_address="Barishal, Bangladesh",
        total_amount=Decimal("200000.00"),
        status=Order.Status.PENDING,
    )

    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=2,
        price=product.price,
    )

    product.stock = 8
    product.save(update_fields=["stock"])

    response = authenticated_customer.post(
        f"/api/orders/{order.id}/cancel/"
    )

    assert response.status_code == 200

    order.refresh_from_db()
    product.refresh_from_db()

    assert order.status == Order.Status.CANCELLED
    assert product.stock == 10


def test_user_cannot_cancel_non_pending_order(
    authenticated_customer,
    customer,
    product,
):
    order = Order.objects.create(
        user=customer,
        shipping_address="Barishal, Bangladesh",
        total_amount=product.price,
        status=Order.Status.CONFIRMED,
    )

    response = authenticated_customer.post(
        f"/api/orders/{order.id}/cancel/"
    )

    assert response.status_code == 400
    assert (
        response.data["detail"]
        == "Only pending orders can be cancelled."
    )


def test_user_cannot_cancel_another_users_order(
    authenticated_customer,
    customer_two,
    product,
):
    order = Order.objects.create(
        user=customer_two,
        shipping_address="Dhaka, Bangladesh",
        total_amount=product.price,
        status=Order.Status.PENDING,
    )

    response = authenticated_customer.post(
        f"/api/orders/{order.id}/cancel/"
    )

    assert response.status_code == 404


def test_unauthenticated_user_cannot_cancel_order(
    api_client,
    customer,
    product,
):
    order = Order.objects.create(
        user=customer,
        shipping_address="Dhaka, Bangladesh",
        total_amount=product.price,
        status=Order.Status.PENDING,
    )

    response = api_client.post(
        f"/api/orders/{order.id}/cancel/"
    )

    assert response.status_code == 401


def test_admin_can_view_all_orders(
    authenticated_admin,
    customer,
    customer_two,
    product,
):
    order_one = Order.objects.create(
        user=customer,
        shipping_address="Barishal, Bangladesh",
        total_amount=product.price,
    )

    order_two = Order.objects.create(
        user=customer_two,
        shipping_address="Dhaka, Bangladesh",
        total_amount=product.price,
    )

    response = authenticated_admin.get(
        "/api/orders/admin/"
    )

    assert response.status_code == 200

    returned_ids = {
        order["id"]
        for order in response.data
    }

    assert order_one.id in returned_ids
    assert order_two.id in returned_ids


def test_customer_cannot_view_admin_orders(
    authenticated_customer,
):
    response = authenticated_customer.get(
        "/api/orders/admin/"
    )

    assert response.status_code == 200
    assert response.data == []


def test_seller_cannot_view_admin_orders(
    authenticated_seller,
):
    response = authenticated_seller.get(
        "/api/orders/admin/"
    )

    assert response.status_code == 200
    assert response.data == []


def test_admin_can_update_order_status(
    authenticated_admin,
    customer,
    product,
):
    order = Order.objects.create(
        user=customer,
        shipping_address="Barishal, Bangladesh",
        total_amount=product.price,
        status=Order.Status.PENDING,
    )

    response = authenticated_admin.patch(
        f"/api/orders/admin/{order.id}/status/",
        {
            "status": "CONFIRMED",
        },
        format="json",
    )

    assert response.status_code == 200

    order.refresh_from_db()

    assert order.status == Order.Status.CONFIRMED


def test_admin_can_cancel_order_and_restore_stock(
    authenticated_admin,
    customer,
    product,
):
    product.stock = 8
    product.save(update_fields=["stock"])

    order = Order.objects.create(
        user=customer,
        shipping_address="Barishal, Bangladesh",
        total_amount=Decimal("200000.00"),
        status=Order.Status.CONFIRMED,
    )

    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=2,
        price=product.price,
    )

    response = authenticated_admin.patch(
        f"/api/orders/admin/{order.id}/status/",
        {
            "status": "CANCELLED",
        },
        format="json",
    )

    assert response.status_code == 200

    order.refresh_from_db()
    product.refresh_from_db()

    assert order.status == Order.Status.CANCELLED
    assert product.stock == 10


def test_admin_cannot_make_invalid_status_transition(
    authenticated_admin,
    customer,
    product,
):
    order = Order.objects.create(
        user=customer,
        shipping_address="Dhaka, Bangladesh",
        total_amount=product.price,
        status=Order.Status.PENDING,
    )

    response = authenticated_admin.patch(
        f"/api/orders/admin/{order.id}/status/",
        {
            "status": "DELIVERED",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "Cannot change order status" in str(
        response.data
    )


def test_admin_cannot_change_delivered_order_status(
    authenticated_admin,
    customer,
    product,
):
    order = Order.objects.create(
        user=customer,
        shipping_address="Dhaka, Bangladesh",
        total_amount=product.price,
        status=Order.Status.DELIVERED,
    )

    response = authenticated_admin.patch(
        f"/api/orders/admin/{order.id}/status/",
        {
            "status": "CANCELLED",
        },
        format="json",
    )

    assert response.status_code == 400


def test_seller_can_view_orders_containing_own_products(
    authenticated_seller,
    customer,
    seller,
    product,
):
    order = Order.objects.create(
        user=customer,
        shipping_address="Barishal, Bangladesh",
        total_amount=product.price,
    )

    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1,
        price=product.price,
    )

    response = authenticated_seller.get(
        "/api/orders/seller/"
    )

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["id"] == order.id


def test_seller_cannot_view_orders_without_own_products(
    authenticated_seller,
    customer,
    seller_two,
    category,
):
    other_product = Product.objects.create(
        name="Other Product",
        description="Other seller product",
        price=Decimal("50000.00"),
        stock=10,
        category=category,
        seller=seller_two,
        is_active=True,
    )

    order = Order.objects.create(
        user=customer,
        shipping_address="Dhaka, Bangladesh",
        total_amount=other_product.price,
    )

    OrderItem.objects.create(
        order=order,
        product=other_product,
        quantity=1,
        price=other_product.price,
    )

    response = authenticated_seller.get(
        "/api/orders/seller/"
    )

    assert response.status_code == 200
    assert response.data == []


def test_customer_cannot_view_seller_orders(
    authenticated_customer,
):
    response = authenticated_customer.get(
        "/api/orders/seller/"
    )

    assert response.status_code == 200
    assert response.data == []


def test_seller_can_update_order_status(
    authenticated_seller,
    customer,
    product,
):
    order = Order.objects.create(
        user=customer,
        shipping_address="Barishal, Bangladesh",
        total_amount=product.price,
        status=Order.Status.PENDING,
    )

    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1,
        price=product.price,
    )

    response = authenticated_seller.patch(
        f"/api/orders/seller/{order.id}/status/",
        {
            "status": "CONFIRMED",
        },
        format="json",
    )

    assert response.status_code == 200

    order.refresh_from_db()

    assert order.status == Order.Status.CONFIRMED


def test_seller_cannot_update_order_without_own_product(
    authenticated_seller,
    customer,
    seller_two,
    category,
):
    other_product = Product.objects.create(
        name="Other Seller Product",
        description="Product of another seller",
        price=Decimal("50000.00"),
        stock=10,
        category=category,
        seller=seller_two,
        is_active=True,
    )

    order = Order.objects.create(
        user=customer,
        shipping_address="Dhaka, Bangladesh",
        total_amount=other_product.price,
        status=Order.Status.PENDING,
    )

    OrderItem.objects.create(
        order=order,
        product=other_product,
        quantity=1,
        price=other_product.price,
    )

    response = authenticated_seller.patch(
        f"/api/orders/seller/{order.id}/status/",
        {
            "status": "CONFIRMED",
        },
        format="json",
    )

    assert response.status_code == 404


def test_seller_cannot_update_invalid_order_status(
    authenticated_seller,
    customer,
    product,
):
    order = Order.objects.create(
        user=customer,
        shipping_address="Dhaka, Bangladesh",
        total_amount=product.price,
        status=Order.Status.PENDING,
    )

    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1,
        price=product.price,
    )

    response = authenticated_seller.patch(
        f"/api/orders/seller/{order.id}/status/",
        {
            "status": "DELIVERED",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "Cannot change order status" in str(
        response.data
    )