# Generated by Django 3.0.7 on 2020-07-10 06:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("wilt_til", "0008_auto_20200709_2126"),
    ]

    operations = [
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.AutoField(
                        primary_key=True, serialize=False, verbose_name="tag id"
                    ),
                ),
                ("name", models.CharField(max_length=50)),
            ],
            options={
                "verbose_name": "태그",
                "verbose_name_plural": "태그",
                "db_table": "tag",
            },
        ),
        migrations.CreateModel(
            name="TilTag",
            fields=[
                (
                    "id",
                    models.AutoField(
                        primary_key=True, serialize=False, verbose_name="tiltag id"
                    ),
                ),
                (
                    "tag_name",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="wilt_til.Tag"
                    ),
                ),
                (
                    "til",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="wilt_til.Til"
                    ),
                ),
            ],
            options={
                "verbose_name": "TIL태그",
                "verbose_name_plural": "TIL태그",
                "db_table": "tiltag",
            },
        ),
    ]
