# Generated by Django 3.0.7 on 2020-07-21 08:59

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Policy",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "terms_of_service",
                    models.TextField(
                        blank=True, null=True, verbose_name="Terms of Service"
                    ),
                ),
                (
                    "privacy_statement",
                    models.TextField(
                        blank=True, null=True, verbose_name="Privacy Statement"
                    ),
                ),
                (
                    "date_created",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="date created",
                    ),
                ),
            ],
            options={"db_table": "wilt_policy", "ordering": ["-date_created"],},
        ),
    ]