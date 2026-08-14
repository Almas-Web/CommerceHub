import pytest
from decimal import Decimal

from rest_framework.test import APIClient

from users.models import CustomUser
from categories.models import Category
from products.models import Product
from orders.models import Order, OrderItem
from .models import Payment


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def customer(db):
    return CustomUser.objects.create_user(
        username="payment_customer",
        email="payment_customer@example.com",
        password="TestPass123!",
        role=CustomUser.Role.CUSTOMER,
        is_verified=True,
    )


@pytest.fixture
def customer_two(db):
    return CustomUser.objects.create_user(
        username="payment_customer_two",
        email="payment_customer_two@example.com",
        password="TestPass123!",
        role=CustomUser.Role.CUSTOMER,
        is_verified=True,
    )


@pytest.fixture
def admin(db):
    return CustomUser.objects.create_user(
        username="payment_admin",
        email="payment_admin@example.com",
        password="TestPass123!",
        role=CustomUser.Role.ADMIN,
        is_verified=True,
    )


@pytest.fixture
def seller(db):
    return CustomUser.objects.create_user(
        username="payment_seller",
        email="payment_seller@example.com",
        password="TestPass123!",
        role=CustomUser.Role.SELLER,
        is_verified=True,
    )


@pytest.fixture
def category(db):
    return Category.objects.create(
        name="Payment Electronics",
        description="Payment test category",
    )


@pytest.fixture
def product(db, seller, category):
    return Product.objects.create(
        name="Payment Test Product",
        description="Product for payment testing",
        price=Decimal("5000.00"),
        stock=10,
        category=category,
        seller=seller,
        is_active=True,
    )


@pytest.fixture
def order(db, customer, product):
    order = Order.objects.create(
        user=customer,
        status=Order.Status.PENDING,
        total_amount=Decimal("10000.00"),
        shipping_address="Barishal, Bangladesh",
    )

    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=2,
        price=Decimal("5000.00"),
    )

    return order


@pytest.fixture
def cancelled_order(db, customer, product):
    order = Order.objects.create(
        user=customer,
        status=Order.Status.CANCELLED,
        total_amount=Decimal("10000.00"),
        shipping_address="Barishal, Bangladesh",
    )

    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=2,
        price=Decimal("5000.00"),
    )

    return order


@pytest.fixture
def authenticated_customer(api_client, customer):
    api_client.force_authenticate(user=customer)
    return api_client


@pytest.fixture
def authenticated_customer_two(api_client, customer_two):
    api_client.force_authenticate(user=customer_two)
    return api_client


@pytest.fixture
def authenticated_admin(api_client, admin):
    api_client.force_authenticate(user=admin)
    return api_client


def test_unauthenticated_user_cannot_create_payment(
    api_client,
):
    response = api_client.post(
        "/api/payments/",
        {
            "order": 1,
            "method": "CARD",
            "transaction_id": "TXN-UNAUTH-001",
        },
        format="json",
    )

    assert response.status_code == 401


def test_authenticated_user_cannot_create_payment_without_order(
    authenticated_customer,
):
    response = authenticated_customer.post(
        "/api/payments/",
        {
            "method": "CARD",
            "transaction_id": "TXN-001",
        },
        format="json",
    )

    assert response.status_code == 400
    assert response.data["detail"] == "Order is required."


def test_user_cannot_pay_nonexistent_order(
    authenticated_customer,
):
    response = authenticated_customer.post(
        "/api/payments/",
        {
            "order": 999999,
            "method": "CARD",
            "transaction_id": "TXN-002",
        },
        format="json",
    )

    assert response.status_code == 404
    assert response.data["detail"] == "Order not found."


def test_user_cannot_pay_another_users_order(
    authenticated_customer_two,
    order,
):
    response = authenticated_customer_two.post(
        "/api/payments/",
        {
            "order": order.id,
            "method": "CARD",
            "transaction_id": "TXN-003",
        },
        format="json",
    )

    assert response.status_code == 404


def test_cancelled_order_cannot_be_paid(
    authenticated_customer,
    cancelled_order,
):
    response = authenticated_customer.post(
        "/api/payments/",
        {
            "order": cancelled_order.id,
            "method": "CARD",
            "transaction_id": "TXN-004",
        },
        format="json",
    )

    assert response.status_code == 400
    assert (
        response.data["detail"]
        == "Cancelled orders cannot be paid."
    )


def test_payment_method_is_required(
    authenticated_customer,
    order,
):
    response = authenticated_customer.post(
        "/api/payments/",
        {
            "order": order.id,
            "transaction_id": "TXN-005",
        },
        format="json",
    )

    assert response.status_code == 400
    assert (
        response.data["detail"]
        == "Payment method is required."
    )


def test_transaction_id_is_required(
    authenticated_customer,
    order,
):
    response = authenticated_customer.post(
        "/api/payments/",
        {
            "order": order.id,
            "method": "CARD",
        },
        format="json",
    )

    assert response.status_code == 400
    assert (
        response.data["detail"]
        == "Transaction ID is required."
    )


def test_customer_can_create_payment(
    authenticated_customer,
    customer,
    order,
):
    response = authenticated_customer.post(
        "/api/payments/",
        {
            "order": order.id,
            "method": "CARD",
            "transaction_id": "TXN-SUCCESS-001",
        },
        format="json",
    )

    assert response.status_code == 201

    payment = Payment.objects.get(
        id=response.data["id"]
    )

    assert payment.order == order
    assert payment.user == customer
    assert payment.transaction_id == "TXN-SUCCESS-001"
    assert payment.amount == Decimal("10000.00")
    assert payment.method == Payment.Method.CARD
    assert payment.status == Payment.Status.PENDING

    assert response.data["order"] == order.id
    assert response.data["user"] == customer.id
    assert response.data["order_total"] == "10000.00"
    assert response.data["status"] == "PENDING"


def test_payment_amount_matches_order_total(
    authenticated_customer,
    order,
):
    response = authenticated_customer.post(
        "/api/payments/",
        {
            "order": order.id,
            "method": "CASH",
            "transaction_id": "TXN-AMOUNT-001",
        },
        format="json",
    )

    assert response.status_code == 201

    payment = Payment.objects.get(
        id=response.data["id"]
    )

    assert payment.amount == order.total_amount


def test_payment_starts_with_pending_status(
    authenticated_customer,
    order,
):
    response = authenticated_customer.post(
        "/api/payments/",
        {
            "order": order.id,
            "method": "MOBILE_BANKING",
            "transaction_id": "TXN-PENDING-001",
        },
        format="json",
    )

    assert response.status_code == 201

    payment = Payment.objects.get(
        id=response.data["id"]
    )

    assert payment.status == Payment.Status.PENDING


def test_payment_transaction_id_must_be_unique(
    customer,
    order,
):
    Payment.objects.create(
        order=order,
        user=customer,
        transaction_id="TXN-DUPLICATE-001",
        amount=order.total_amount,
        method=Payment.Method.CARD,
        status=Payment.Status.PENDING,
    )

    second_order = Order.objects.create(
        user=customer,
        status=Order.Status.PENDING,
        total_amount=Decimal("5000.00"),
        shipping_address="Dhaka, Bangladesh",
    )

    with pytest.raises(Exception):
        Payment.objects.create(
            order=second_order,
            user=customer,
            transaction_id="TXN-DUPLICATE-001",
            amount=second_order.total_amount,
            method=Payment.Method.CARD,
            status=Payment.Status.PENDING,
        )


def test_user_cannot_create_second_payment_for_same_order(
    authenticated_customer,
    order,
):
    Payment.objects.create(
        order=order,
        user=order.user,
        transaction_id="TXN-EXISTING-001",
        amount=order.total_amount,
        method=Payment.Method.CARD,
        status=Payment.Status.PENDING,
    )

    response = authenticated_customer.post(
        "/api/payments/",
        {
            "order": order.id,
            "method": "CASH",
            "transaction_id": "TXN-SECOND-001",
        },
        format="json",
    )

    assert response.status_code == 400
    assert (
        response.data["detail"]
        == "Payment already exists for this order."
    )


def test_customer_can_update_own_payment_status_to_success(
    authenticated_customer,
    order,
):
    payment = Payment.objects.create(
        order=order,
        user=order.user,
        transaction_id="TXN-STATUS-001",
        amount=order.total_amount,
        method=Payment.Method.CARD,
        status=Payment.Status.PENDING,
    )

    response = authenticated_customer.patch(
        f"/api/payments/{payment.id}/status/",
        {
            "status": "SUCCESS",
        },
        format="json",
    )

    assert response.status_code == 200

    payment.refresh_from_db()

    assert payment.status == Payment.Status.SUCCESS
    assert response.data["status"] == "SUCCESS"


def test_customer_can_update_own_payment_status_to_failed(
    authenticated_customer,
    order,
):
    payment = Payment.objects.create(
        order=order,
        user=order.user,
        transaction_id="TXN-STATUS-002",
        amount=order.total_amount,
        method=Payment.Method.CARD,
        status=Payment.Status.PENDING,
    )

    response = authenticated_customer.patch(
        f"/api/payments/{payment.id}/status/",
        {
            "status": "FAILED",
        },
        format="json",
    )

    assert response.status_code == 200

    payment.refresh_from_db()

    assert payment.status == Payment.Status.FAILED


def test_success_payment_can_be_refunded(
    authenticated_customer,
    order,
):
    payment = Payment.objects.create(
        order=order,
        user=order.user,
        transaction_id="TXN-REFUND-001",
        amount=order.total_amount,
        method=Payment.Method.CARD,
        status=Payment.Status.SUCCESS,
    )

    response = authenticated_customer.patch(
        f"/api/payments/{payment.id}/status/",
        {
            "status": "REFUNDED",
        },
        format="json",
    )

    assert response.status_code == 200

    payment.refresh_from_db()

    assert payment.status == Payment.Status.REFUNDED


def test_pending_payment_cannot_be_refunded_directly(
    authenticated_customer,
    order,
):
    payment = Payment.objects.create(
        order=order,
        user=order.user,
        transaction_id="TXN-REFUND-002",
        amount=order.total_amount,
        method=Payment.Method.CARD,
        status=Payment.Status.PENDING,
    )

    response = authenticated_customer.patch(
        f"/api/payments/{payment.id}/status/",
        {
            "status": "REFUNDED",
        },
        format="json",
    )

    assert response.status_code == 400


def test_failed_payment_cannot_be_changed_to_success(
    authenticated_customer,
    order,
):
    payment = Payment.objects.create(
        order=order,
        user=order.user,
        transaction_id="TXN-FAILED-001",
        amount=order.total_amount,
        method=Payment.Method.CARD,
        status=Payment.Status.FAILED,
    )

    response = authenticated_customer.patch(
        f"/api/payments/{payment.id}/status/",
        {
            "status": "SUCCESS",
        },
        format="json",
    )

    assert response.status_code == 400


def test_refunded_payment_cannot_be_changed_again(
    authenticated_customer,
    order,
):
    payment = Payment.objects.create(
        order=order,
        user=order.user,
        transaction_id="TXN-REFUNDED-001",
        amount=order.total_amount,
        method=Payment.Method.CARD,
        status=Payment.Status.REFUNDED,
    )

    response = authenticated_customer.patch(
        f"/api/payments/{payment.id}/status/",
        {
            "status": "SUCCESS",
        },
        format="json",
    )

    assert response.status_code == 400


def test_invalid_payment_status_is_rejected(
    authenticated_customer,
    order,
):
    payment = Payment.objects.create(
        order=order,
        user=order.user,
        transaction_id="TXN-INVALID-001",
        amount=order.total_amount,
        method=Payment.Method.CARD,
        status=Payment.Status.PENDING,
    )

    response = authenticated_customer.patch(
        f"/api/payments/{payment.id}/status/",
        {
            "status": "INVALID_STATUS",
        },
        format="json",
    )

    assert response.status_code == 400
    assert (
        response.data["detail"]
        == "Invalid payment status."
    )


def test_customer_cannot_update_another_users_payment(
    authenticated_customer_two,
    order,
):
    payment = Payment.objects.create(
        order=order,
        user=order.user,
        transaction_id="TXN-OTHER-001",
        amount=order.total_amount,
        method=Payment.Method.CARD,
        status=Payment.Status.PENDING,
    )

    response = authenticated_customer_two.patch(
        f"/api/payments/{payment.id}/status/",
        {
            "status": "SUCCESS",
        },
        format="json",
    )

    assert response.status_code == 404


def test_admin_can_update_any_payment_status(
    authenticated_admin,
    order,
):
    payment = Payment.objects.create(
        order=order,
        user=order.user,
        transaction_id="TXN-ADMIN-001",
        amount=order.total_amount,
        method=Payment.Method.CARD,
        status=Payment.Status.PENDING,
    )

    response = authenticated_admin.patch(
        f"/api/payments/{payment.id}/status/",
        {
            "status": "SUCCESS",
        },
        format="json",
    )

    assert response.status_code == 200

    payment.refresh_from_db()

    assert payment.status == Payment.Status.SUCCESS


def test_unauthenticated_user_cannot_update_payment(
    api_client,
    order,
):
    payment = Payment.objects.create(
        order=order,
        user=order.user,
        transaction_id="TXN-UNAUTH-STATUS-001",
        amount=order.total_amount,
        method=Payment.Method.CARD,
        status=Payment.Status.PENDING,
    )

    response = api_client.patch(
        f"/api/payments/{payment.id}/status/",
        {
            "status": "SUCCESS",
        },
        format="json",
    )

    assert response.status_code == 401