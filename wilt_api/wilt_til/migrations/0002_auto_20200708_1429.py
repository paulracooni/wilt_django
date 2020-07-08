# Generated by Django 3.0.7 on 2020-07-08 05:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("wilt_user", "0001_initial"),
        ("wilt_til", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="til",
            name="date_created",
            field=models.DateTimeField(auto_now_add=True, verbose_name="date created"),
        ),
        migrations.CreateModel(
            name="Clap",
            fields=[
                (
                    "id",
                    models.AutoField(
                        primary_key=True, serialize=False, verbose_name="clap id"
                    ),
                ),
                (
                    "date_created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="date created"
                    ),
                ),
                (
                    "til",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="wilt_til.Til"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="wilt_user.WiltUser",
                    ),
                ),
            ],
            options={
                "verbose_name": "clap",
                "verbose_name_plural": "claps",
                "unique_together": {("user", "til")},
            },
        ),
        migrations.CreateModel(
            name="Bookmark",
            fields=[
                (
                    "id",
                    models.AutoField(
                        primary_key=True, serialize=False, verbose_name="bookmark id"
                    ),
                ),
                (
                    "date_created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="date created"
                    ),
                ),
                (
                    "til",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="wilt_til.Til"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="wilt_user.WiltUser",
                    ),
                ),
            ],
            options={
                "verbose_name": "bookmark",
                "verbose_name_plural": "bookmarks",
                "unique_together": {("user", "til")},
            },
        ),
    ]
