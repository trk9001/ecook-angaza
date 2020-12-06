from django.db import models


class UsageData(models.Model):
    unit_number = models.PositiveIntegerField()
    when = models.DateTimeField()
    type = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
