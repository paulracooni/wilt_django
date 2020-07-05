# Generated by Django 3.0.7 on 2020-07-05 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wilt_user", "0002_auto_20200704_0031"),
    ]

    operations = [
        migrations.AddField(
            model_name="wiltuser",
            name="description",
            field=models.TextField(
                blank=True, null=True, verbose_name="user description"
            ),
        ),
        migrations.AddField(
            model_name="wiltuser",
            name="web_link",
            field=models.TextField(blank=True, null=True, verbose_name="web link"),
        ),
    ]
