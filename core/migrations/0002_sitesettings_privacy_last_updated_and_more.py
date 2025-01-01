# Generated by Django 5.0.8 on 2024-12-15 16:29

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="privacy_last_updated",
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="terms_last_updated",
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]