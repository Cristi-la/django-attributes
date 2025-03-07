# Generated by Django 5.0.7 on 2025-02-24 19:03

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attributes', '0003_attrvalue'),
    ]

    operations = [
        migrations.AddField(
            model_name='attrconfiguration',
            name='count',
            field=models.PositiveIntegerField(default=1, help_text='The number of values for this attribute configuration.', validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
