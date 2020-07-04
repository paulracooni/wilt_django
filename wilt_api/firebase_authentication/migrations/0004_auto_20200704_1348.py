# Generated by Django 3.0.7 on 2020-07-04 04:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("firebase_authentication", "0003_auto_20200704_0020"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="display_name",
            field=models.CharField(
                blank=True,
                default="",
                max_length=20,
                unique=True,
                verbose_name="display name",
            ),
        ),
    ]
