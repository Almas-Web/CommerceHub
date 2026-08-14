from datetime import timedelta
from unittest.mock import patch

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from .models import CustomUser


pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def verified_user():
    return CustomUser.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="TestPassword123",
        role=CustomUser.Role.CUSTOMER,
        is_verified=True,
    )


@pytest.fixture
def unverified_user():
    return CustomUser.objects.create_user(
        username="unverified",
        email="unverified@example.com",
        password="TestPassword123",
        role=CustomUser.Role.CUSTOMER,
        is_verified=False,
        verification_token="verification-token",
    )


# Signup

@patch("users.serializers.send_verification_email_task.delay")
def test_signup_success(mock_task, api_client):
    response = api_client.post(
        reverse("signup"),
        {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "TestPassword123",
            "role": "CUSTOMER",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    user = CustomUser.objects.get(
        email="newuser@example.com"
    )

    assert user.username == "newuser"
    assert user.role == "CUSTOMER"
    assert user.is_verified is False
    assert user.verification_token
    assert user.check_password("TestPassword123")

    mock_task.assert_called_once()


@patch("users.serializers.send_verification_email_task.delay")
def test_signup_password_is_hashed(mock_task, api_client):
    raw_password = "TestPassword123"

    response = api_client.post(
        reverse("signup"),
        {
            "username": "hashuser",
            "email": "hash@example.com",
            "password": raw_password,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    user = CustomUser.objects.get(
        email="hash@example.com"
    )

    assert user.password != raw_password
    assert user.check_password(raw_password)


# Email Verification

def test_verify_email_success(api_client, unverified_user):
    response = api_client.get(
        reverse(
            "verify_email",
            kwargs={
                "token": unverified_user.verification_token
            },
        )
    )

    assert response.status_code == status.HTTP_200_OK

    unverified_user.refresh_from_db()

    assert unverified_user.is_verified is True
    assert unverified_user.verification_token is None


def test_verify_email_invalid_token(api_client):
    response = api_client.get(
        reverse(
            "verify_email",
            kwargs={
                "token": "invalid-token"
            },
        )
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["details"] == "Invalid token"


def test_verify_email_already_verified(api_client, verified_user):
    verified_user.verification_token = "already-verified-token"

    verified_user.save(
        update_fields=["verification_token"]
    )

    response = api_client.get(
        reverse(
            "verify_email",
            kwargs={
                "token": "already-verified-token"
            },
        )
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["details"] == "Email already verified!"


# Resend Verification

@patch("users.views.send_verification_email_task.delay")
def test_resend_verification_success(
    mock_task,
    api_client,
    unverified_user,
):
    old_token = unverified_user.verification_token

    response = api_client.post(
        reverse("resend_verification"),
        {
            "email": unverified_user.email
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    unverified_user.refresh_from_db()

    assert unverified_user.verification_token
    assert unverified_user.verification_token != old_token

    mock_task.assert_called_once()


def test_resend_verification_without_email(api_client):
    response = api_client.post(
        reverse("resend_verification"),
        {},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["details"] == "Email is required!"


def test_resend_verification_user_not_found(api_client):
    response = api_client.post(
        reverse("resend_verification"),
        {
            "email": "notfound@example.com"
        },
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["details"] == (
        "User with this email doesn't exist!"
    )


def test_resend_verification_already_verified(
    api_client,
    verified_user,
):
    response = api_client.post(
        reverse("resend_verification"),
        {
            "email": verified_user.email
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["details"] == "Email already verified!"


# Login

def test_login_success(api_client, verified_user):
    response = api_client.post(
        reverse("login"),
        {
            "email": verified_user.email,
            "password": "TestPassword123",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    assert "access_token" in response.data
    assert "refresh_token" in response.data


def test_login_unverified_user(
    api_client,
    unverified_user,
):
    response = api_client.post(
        reverse("login"),
        {
            "email": unverified_user.email,
            "password": "TestPassword123",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    assert response.data["details"] == (
        "Email is not verified yet!"
    )


def test_login_wrong_password(
    api_client,
    verified_user,
):
    response = api_client.post(
        reverse("login"),
        {
            "email": verified_user.email,
            "password": "WrongPassword123",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data["details"] == "Invalid credentials"


def test_login_nonexistent_user(api_client):
    response = api_client.post(
        reverse("login"),
        {
            "email": "unknown@example.com",
            "password": "TestPassword123",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data["details"] == "Invalid credentials"


# Profile

def test_profile_requires_authentication(api_client):
    response = api_client.get(
        reverse("profile")
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_profile(
    api_client,
    verified_user,
):
    api_client.force_authenticate(
        user=verified_user
    )

    response = api_client.get(
        reverse("profile")
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["username"] == verified_user.username
    assert response.data["email"] == verified_user.email
    assert response.data["role"] == verified_user.role


def test_update_profile(
    api_client,
    verified_user,
):
    api_client.force_authenticate(
        user=verified_user
    )

    response = api_client.patch(
        reverse("profile"),
        {
            "bio": "Python Backend Developer"
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    verified_user.refresh_from_db()

    assert verified_user.bio == "Python Backend Developer"


def test_profile_update_unauthenticated(api_client):
    response = api_client.patch(
        reverse("profile"),
        {
            "bio": "Unauthorized update"
        },
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Forgot Password

@patch("users.views.send_password_reset_email_task.delay")
def test_forgot_password_success(
    mock_task,
    api_client,
    verified_user,
):
    response = api_client.post(
        reverse("forgot_password"),
        {
            "email": verified_user.email
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    verified_user.refresh_from_db()

    assert verified_user.password_reset_token
    assert verified_user.password_reset_token_created_at

    mock_task.assert_called_once()


def test_forgot_password_user_not_found(api_client):
    response = api_client.post(
        reverse("forgot_password"),
        {
            "email": "unknown@example.com"
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


# Reset Password

def test_reset_password_success(
    api_client,
    verified_user,
):
    verified_user.password_reset_token = "valid-reset-token"

    verified_user.password_reset_token_created_at = (
        timezone.now()
    )

    verified_user.save(
        update_fields=[
            "password_reset_token",
            "password_reset_token_created_at",
        ]
    )

    response = api_client.post(
        reverse(
            "reset_password",
            kwargs={
                "token": "valid-reset-token"
            },
        ),
        {
            "new_password": "NewPassword123"
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    verified_user.refresh_from_db()

    assert verified_user.check_password(
        "NewPassword123"
    )

    assert verified_user.password_reset_token is None

    assert (
        verified_user.password_reset_token_created_at
        is None
    )


def test_reset_password_invalid_token(api_client):
    response = api_client.post(
        reverse(
            "reset_password",
            kwargs={
                "token": "invalid-token"
            },
        ),
        {
            "new_password": "NewPassword123"
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_reset_password_expired_token(
    api_client,
    verified_user,
):
    verified_user.password_reset_token = "expired-token"

    verified_user.password_reset_token_created_at = (
        timezone.now() - timedelta(hours=2)
    )

    verified_user.save(
        update_fields=[
            "password_reset_token",
            "password_reset_token_created_at",
        ]
    )

    response = api_client.post(
        reverse(
            "reset_password",
            kwargs={
                "token": "expired-token"
            },
        ),
        {
            "new_password": "NewPassword123"
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_reset_password_short_password(
    api_client,
    verified_user,
):
    verified_user.password_reset_token = (
        "short-password-token"
    )

    verified_user.password_reset_token_created_at = (
        timezone.now()
    )

    verified_user.save(
        update_fields=[
            "password_reset_token",
            "password_reset_token_created_at",
        ]
    )

    response = api_client.post(
        reverse(
            "reset_password",
            kwargs={
                "token": "short-password-token"
            },
        ),
        {
            "new_password": "123"
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


# JWT Refresh

def test_refresh_token(
    api_client,
    verified_user,
):
    login_response = api_client.post(
        reverse("login"),
        {
            "email": verified_user.email,
            "password": "TestPassword123",
        },
        format="json",
    )

    assert login_response.status_code == status.HTTP_200_OK

    refresh_token = login_response.data["refresh_token"]

    response = api_client.post(
        reverse("token_refresh"),
        {
            "refresh": refresh_token
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data