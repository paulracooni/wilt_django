# Generated by Django 3.0.7 on 2020-07-22 08:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("wilt_backend", "0003_comment"),
    ]

    operations = [
        migrations.CreateModel(
            name="LogSearch",
            fields=[
                (
                    "id",
                    models.AutoField(
                        primary_key=True, serialize=False, verbose_name="search id"
                    ),
                ),
                ("search_type", models.CharField(max_length=20, verbose_name="type")),
                ("keyword", models.CharField(max_length=50, verbose_name="keyword")),
                (
                    "date_created",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="date created",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "search log",
                "verbose_name_plural": "search logs",
                "db_table": "log_search",
                "ordering": ("date_created",),
            },
        ),
    ]
