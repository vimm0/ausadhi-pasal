from django.db import models

from ..users.models import User


class Product(models.Model):
    name = models.CharField(max_length=225)
    price_per_unit = models.DecimalField(max_digits=25, decimal_places=2)
    supplier = models.OneToOneField(User, on_delete=models.CASCADE)
