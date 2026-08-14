from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):

    class Role(models.TextChoices):
        CUSTOMER = 'CUSTOMER', 'Customer'
        SELLER = 'SELLER', 'Seller'
        ADMIN = 'ADMIN', 'Admin'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER
    )

    is_verified = models.BooleanField(default=False)

    verification_token = models.CharField(
        max_length=32,
        blank=True,
        null=True
    )

    password_reset_token = models.CharField(
        max_length=64,
        blank=True,
        null=True
    )

    password_reset_token_created_at = models.DateTimeField(
        blank=True,
        null=True
    )

    bio = models.TextField(blank=True)

    def __str__(self):
        return self.username