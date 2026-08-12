from django.db import models
from django.conf import settings


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    stock = models.PositiveIntegerField(default=0)

    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.PROTECT,
        related_name='products'
    )

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='products'
    )

    image = models.ImageField(
        upload_to='product_images/',
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name