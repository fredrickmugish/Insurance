# Generated by Django 5.1.5 on 2025-03-13 08:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("category_name", models.CharField(max_length=100)),
                ("creation_date", models.DateField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Policy",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("policy_name", models.CharField(max_length=200)),
                ("sum_assurance", models.PositiveIntegerField()),
                ("premium", models.PositiveIntegerField()),
                ("tenure", models.PositiveIntegerField()),
                ("creation_date", models.DateField(auto_now=True)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="provider.category",
                    ),
                ),
                (
                    "provider",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="provider_policies",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
