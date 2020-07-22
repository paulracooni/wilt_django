# Generated by Django 3.0.7 on 2020-07-22 05:51

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("wilt_backend", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userfollow",
            name="date_created",
            field=models.DateTimeField(
                default=django.utils.timezone.now,
                editable=False,
                verbose_name="date created",
            ),
        ),
    ]