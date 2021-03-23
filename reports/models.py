from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class UnitNumber(models.Model):
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    unit_number = models.PositiveIntegerField(unique=True)
    description = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        if self.name is not None:
            return self.name + ' - ' + str(self.unit_number)

        return str(self.unit_number)


class UsageData(models.Model):
    unit_number = models.PositiveIntegerField()
    when_datetime = models.DateTimeField()
    data_type = models.CharField(max_length=255)
    data_value = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        types = {}
        types['219'] = 'Serial Number'
        types['220'] = 'Average Battery Voltage (Last 12 Hours'
        types['221'] = 'Max Battery Voltage (Last 12 Hours)'
        types['222'] = 'Min Battery Voltage (Last 12 Hours)'
        types['223'] = 'Battery Critical State Count'
        types['224'] = '1 Hour Samples Count'
        types['225'] = 'Lock Mode Entry Count'
        types['226'] = 'Factory Mode Entry Count'
        types['227'] = 'GSM Sync Button Count'
        types['228'] = 'Stove On/Off Count'
        types['229'] = 'Energy Consumed per Hour'
        types['230'] = 'Left Stove Cooktime per Hour'
        types['231'] = 'Right Stove Cooktime per Hour'
        types['232'] = 'Other'

        return types[self.data_type]


class DailyUsageData(models.Model):
    serial_number = models.PositiveIntegerField()
    average_battery_voltage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.00)
    max_battery_voltage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.00)
    min_battery_voltage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.00)
    battery_critical_state_count = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.00)
    one_hour_samples_count = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.00)
    lock_mode_entry_count = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.00)
    factory_mode_entry_count = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.00)
    gsm_sync_button_count = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.00)
    stove_on_off_count = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.00)
    daily_power_consumption = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.00)
    left_stove_cooktime = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.00)
    right_stove_cooktime = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.00)
    daily_cooking_time = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.00)
    average_power_consumption_per_use = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.00)
    average_cooking_time_per_use = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.00)
    when_date = models.DateField(null=True)
    others = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
