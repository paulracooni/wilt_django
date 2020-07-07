# Generated by Django 3.0.7 on 2020-07-07 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("firebase_authentication", "0005_auto_20200704_1348"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="display_name",
            field=models.CharField(
                blank=True,
                max_length=20,
                null=True,
                unique=True,
                verbose_name="display name",
            ),
        ),
    ]
