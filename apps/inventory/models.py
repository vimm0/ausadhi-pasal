from django.db import models

# from jsonfield import JSONField
from apps.users.models import User

STATUS = (
    ('Pending', 'Pending'),
    ('Failed', 'Failed'),
    ('Succeed', 'Succeed')
)

METHOD = (
    ('PayPal', 'PayPal'),

)


class Payment(models.Model):
    user = models.ForeignKey(User, related_name='payments', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    method = models.CharField(max_length=10, choices=METHOD)
    # data = JSONField()
    status = models.CharField(max_length=10, choices=STATUS)
    date = models.DateTimeField(auto_now=False, auto_now_add=False)
