from django.db import models
from django.conf import settings
from orders.models import Order


class Payment(models.Model):

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        SUCCESS = 'SUCCESS', 'Success'
        FAILED = 'FAILED', 'Failed'
        REFUNDED = 'REFUNDED', 'Refunded'

    class Method(models.TextChoices):
        CARD = 'CARD', 'Card'
        CASH = 'CASH', 'Cash'
        MOBILE_BANKING = 'MOBILE_BANKING', 'Mobile Banking'

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='payment'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    transaction_id = models.CharField(
        max_length=255,
        unique=True
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    method = models.CharField(
        max_length=30,
        choices=Method.choices
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.transaction_id