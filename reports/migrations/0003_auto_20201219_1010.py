# Generated by Django 3.1.4 on 2020-12-19 10:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0002_unitnumber'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usagedata',
            old_name='type',
            new_name='data_type',
        ),
        migrations.RenameField(
            model_name='usagedata',
            old_name='value',
            new_name='data_value',
        ),
        migrations.RenameField(
            model_name='usagedata',
            old_name='when',
            new_name='when_datetime',
        ),
    ]