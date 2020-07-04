# Generated by Django 3.0.7 on 2020-07-03 15:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import wilt_user.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("firebase_authentication", "0003_auto_20200704_0020"),
    ]

    operations = [
        migrations.CreateModel(
            name="WiltUser",
            fields=[
                (
                    "user_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "company_name",
                    models.CharField(
                        blank=True, max_length=20, verbose_name="company name"
                    ),
                ),
                (
                    "job_title",
                    models.CharField(
                        blank=True, max_length=20, verbose_name="job title"
                    ),
                ),
                (
                    "career_year",
                    models.DecimalField(
                        blank=True,
                        decimal_places=0,
                        max_digits=3,
                        verbose_name="company name",
                    ),
                ),
            ],
            options={"verbose_name": "user", "verbose_name_plural": "users",},
            bases=("firebase_authentication.user",),
            managers=[("objects", wilt_user.managers.WiltUserManager()),],
        ),
    ]