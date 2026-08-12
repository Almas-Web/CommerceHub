from django.db import models
from django.conf import settings
from products.models import Product


class Review(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    rating = models.PositiveIntegerField()

    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'user'],
                name='unique_product_review_by_user'
            )
        ]

    def __str__(self):
        return f"{self.product.name} - {self.rating}/5"