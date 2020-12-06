from django.db import models


class UsageData(models.Model):
    unit_number = models.PositiveIntegerField()
    when = models.DateTimeField()
    type = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        types = []
        types[219] = 'Serial Number'
        types[220] = 'Average Battery Voltage (Last 12 Hours'
        types[221] = 'Max Battery Voltage (Last 12 Hours)'
        types[222] = 'Min Battery Voltage (Last 12 Hours)'
        types[223] = 'Battery Critical State Count'
        types[224] = '1 Hour Samples Count'
        types[225] = 'Lock Mode Entry Count'
        types[226] = 'Factory Mode Entry Count'
        types[227] = 'GSM Sync Button Count'
        types[228] = 'Stove On/Off Count'
        types[229] = 'Energy Consumed per Hour'
        types[230] = 'Left Stove Cooktime per Hour'
        types[231] = 'Right Stove Cooktime per Hour'

        return types[self.type]
