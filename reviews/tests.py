import pytest
from decimal import Decimal

from rest_framework.test import APIClient

from users.models import CustomUser
from categories.models import Category
from products.models import Product
from orders.models import Order, OrderItem
from reviews.models import Review


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def customer(db):
    return CustomUser.objects.create_user(
        username="review_customer",
        email="customer@example.com",
        password="CustomerPass123!",
        role="CUSTOMER",
    )


@pytest.fixture
def another_customer(db):
    return CustomUser.objects.create_user(
        username="another_customer",
        email="another@example.com",
        password="CustomerPass123!",
        role="CUSTOMER",
    )


@pytest.fixture
def seller(db):
    return CustomUser.objects.create_user(
        username="review_seller",
        email="seller@example.com",
        password="SellerPass123!",
        role="SELLER",
    )


@pytest.fixture
def admin(db):
    return CustomUser.objects.create_user(
        username="review_admin",
        email="admin@example.com",
        password="AdminPass123!",
        role="ADMIN",
        is_staff=True,
        is_superuser=True,
    )


@pytest.fixture
def category(db):
    return Category.objects.create(
        name="Review Category"
    )


@pytest.fixture
def product(db, category, seller):
    return Product.objects.create(
        name="Review Product",
        description="Product for review tests",
        price=Decimal("1000.00"),
        stock=10,
        category=category,
        seller=seller,
    )


@pytest.fixture
def delivered_order(db, customer, product):
    order = Order.objects.create(
        user=customer,
        status=Order.Status.DELIVERED,
        total_amount=Decimal("1000.00"),
    )

    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1,
        price=product.price,
    )

    return order


@pytest.fixture
def pending_order(db, customer, product):
    order = Order.objects.create(
        user=customer,
        status=Order.Status.PENDING,
        total_amount=Decimal("1000.00"),
    )

    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1,
        price=product.price,
    )

    return order


@pytest.fixture
def review(db, customer, product):
    return Review.objects.create(
        product=product,
        user=customer,
        rating=5,
        comment="Excellent product!",
    )


@pytest.mark.django_db
def test_customer_can_review_delivered_product(
    api_client,
    customer,
    product,
    delivered_order,
):
    api_client.force_authenticate(user=customer)

    response = api_client.post(
        "/api/reviews/create/",
        {
            "product": product.pk,
            "rating": 5,
            "comment": "Excellent product!",
        },
        format="json",
    )

    assert response.status_code == 201

    assert Review.objects.filter(
        product=product,
        user=customer,
    ).exists()


@pytest.mark.django_db
def test_unauthenticated_user_cannot_create_review(
    api_client,
    product,
):
    response = api_client.post(
        "/api/reviews/create/",
        {
            "product": product.pk,
            "rating": 5,
            "comment": "Nice product",
        },
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_seller_cannot_create_review(
    api_client,
    seller,
    product,
):
    api_client.force_authenticate(user=seller)

    response = api_client.post(
        "/api/reviews/create/",
        {
            "product": product.pk,
            "rating": 5,
            "comment": "Nice product",
        },
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_admin_cannot_create_review(
    api_client,
    admin,
    product,
):
    api_client.force_authenticate(user=admin)

    response = api_client.post(
        "/api/reviews/create/",
        {
            "product": product.pk,
            "rating": 5,
            "comment": "Nice product",
        },
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_customer_cannot_review_unpurchased_product(
    api_client,
    customer,
    product,
):
    api_client.force_authenticate(user=customer)

    response = api_client.post(
        "/api/reviews/create/",
        {
            "product": product.pk,
            "rating": 5,
            "comment": "Nice product",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "purchased" in str(response.data).lower()


@pytest.mark.django_db
def test_customer_cannot_review_non_delivered_product(
    api_client,
    customer,
    product,
    pending_order,
):
    api_client.force_authenticate(user=customer)

    response = api_client.post(
        "/api/reviews/create/",
        {
            "product": product.pk,
            "rating": 5,
            "comment": "Nice product",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "purchased" in str(response.data).lower()


@pytest.mark.django_db
def test_customer_cannot_create_duplicate_review(
    api_client,
    customer,
    product,
    delivered_order,
    review,
):
    api_client.force_authenticate(user=customer)

    response = api_client.post(
        "/api/reviews/create/",
        {
            "product": product.pk,
            "rating": 4,
            "comment": "Another review",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "already reviewed" in str(response.data).lower()


@pytest.mark.django_db
@pytest.mark.parametrize("rating", [0, -1, 6, 10])
def test_rating_must_be_between_1_and_5(
    api_client,
    customer,
    product,
    delivered_order,
    rating,
):
    api_client.force_authenticate(user=customer)

    response = api_client.post(
        "/api/reviews/create/",
        {
            "product": product.pk,
            "rating": rating,
            "comment": "Invalid rating",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "rating" in response.data


@pytest.mark.django_db
@pytest.mark.parametrize("rating", [1, 2, 3, 4, 5])
def test_valid_rating_is_accepted(
    api_client,
    customer,
    product,
    delivered_order,
    rating,
):
    api_client.force_authenticate(user=customer)

    response = api_client.post(
        "/api/reviews/create/",
        {
            "product": product.pk,
            "rating": rating,
            "comment": "Valid rating",
        },
        format="json",
    )

    assert response.status_code == 201


@pytest.mark.django_db
def test_authenticated_user_can_view_product_reviews(
    api_client,
    customer,
    product,
    review,
):
    api_client.force_authenticate(user=customer)

    response = api_client.get(
        f"/api/reviews/product/{product.pk}/"
    )

    assert response.status_code == 200
    assert len(response.data) == 1


@pytest.mark.django_db
def test_product_review_list_contains_review_data(
    api_client,
    customer,
    product,
    review,
):
    api_client.force_authenticate(user=customer)

    response = api_client.get(
        f"/api/reviews/product/{product.pk}/"
    )

    assert response.status_code == 200

    data = response.data[0]

    assert data["product"] == product.pk
    assert data["user"] == customer.pk
    assert data["rating"] == 5
    assert data["comment"] == "Excellent product!"


@pytest.mark.django_db
def test_unauthenticated_user_cannot_view_product_reviews(
    api_client,
    product,
    review,
):
    response = api_client.get(
        f"/api/reviews/product/{product.pk}/"
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_product_review_list_returns_only_selected_product_reviews(
    api_client,
    customer,
    seller,
    category,
    product,
    review,
):
    another_product = Product.objects.create(
        name="Another Product",
        description="Another product",
        price=Decimal("2000.00"),
        stock=5,
        category=category,
        seller=seller,
    )

    Review.objects.create(
        product=another_product,
        user=customer,
        rating=4,
        comment="Another review",
    )

    api_client.force_authenticate(user=customer)

    response = api_client.get(
        f"/api/reviews/product/{product.pk}/"
    )

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["product"] == product.pk


@pytest.mark.django_db
def test_customer_can_update_own_review(
    api_client,
    customer,
    review,
):
    api_client.force_authenticate(user=customer)

    response = api_client.patch(
        f"/api/reviews/{review.pk}/update/",
        {
            "rating": 4,
            "comment": "Updated review",
        },
        format="json",
    )

    assert response.status_code == 200

    review.refresh_from_db()

    assert review.rating == 4
    assert review.comment == "Updated review"


@pytest.mark.django_db
def test_customer_cannot_update_other_users_review(
    api_client,
    another_customer,
    review,
):
    api_client.force_authenticate(user=another_customer)

    response = api_client.patch(
        f"/api/reviews/{review.pk}/update/",
        {
            "rating": 1,
            "comment": "Trying to change another review",
        },
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_customer_cannot_change_product_when_updating_review(
    api_client,
    customer,
    review,
    category,
    seller,
):
    original_product = review.product

    another_product = Product.objects.create(
        name="Another Product",
        description="Another product",
        price=Decimal("2000.00"),
        stock=5,
        category=category,
        seller=seller,
    )

    api_client.force_authenticate(user=customer)

    response = api_client.patch(
        f"/api/reviews/{review.pk}/update/",
        {
            "product": another_product.pk,
            "rating": 4,
            "comment": "Updated review",
        },
        format="json",
    )

    assert response.status_code == 200

    review.refresh_from_db()

    assert review.product == original_product
    assert review.product != another_product
    assert review.rating == 4
    assert review.comment == "Updated review"


@pytest.mark.django_db
def test_customer_cannot_update_review_with_invalid_rating(
    api_client,
    customer,
    review,
):
    api_client.force_authenticate(user=customer)

    response = api_client.patch(
        f"/api/reviews/{review.pk}/update/",
        {
            "rating": 6,
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_customer_can_delete_own_review(
    api_client,
    customer,
    review,
):
    api_client.force_authenticate(user=customer)

    response = api_client.delete(
        f"/api/reviews/{review.pk}/delete/"
    )

    assert response.status_code == 204

    assert not Review.objects.filter(
        pk=review.pk
    ).exists()


@pytest.mark.django_db
def test_customer_cannot_delete_other_users_review(
    api_client,
    another_customer,
    review,
):
    api_client.force_authenticate(user=another_customer)

    response = api_client.delete(
        f"/api/reviews/{review.pk}/delete/"
    )

    assert response.status_code == 404

    assert Review.objects.filter(
        pk=review.pk
    ).exists()


@pytest.mark.django_db
def test_unauthenticated_user_cannot_delete_review(
    api_client,
    review,
):
    response = api_client.delete(
        f"/api/reviews/{review.pk}/delete/"
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_review_unique_product_user_constraint(
    customer,
    product,
    review,
):
    with pytest.raises(Exception):
        Review.objects.create(
            product=product,
            user=customer,
            rating=4,
            comment="Duplicate review",
        )