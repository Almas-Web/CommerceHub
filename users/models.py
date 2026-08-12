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
    bio = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='profile_images/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.username