# Generated by Django 3.0.7 on 2020-07-08 07:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("wilt_user", "0001_initial"),
        ("wilt_til", "0004_auto_20200708_1617"),
    ]

    operations = [
        migrations.AlterField(
            model_name="til",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="wilt_user.WiltUser"
            ),
        ),
    ]
