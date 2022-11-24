from django.db import models
from django.utils import timezone


class Spot(models.Model):
    address = models.CharField(
        max_length=256,
        unique=True,
    )
    lon = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )
    lat = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )
    created_at = models.DateField(
        default=timezone.now,
    )
