# Generated by Django 3.0.7 on 2020-08-28 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wilt_backend', '0007_cheerupsentence'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plant',
            name='satellite',
            field=models.TextField(blank=True, default=None, null=True, verbose_name='satellite'),
        ),
    ]
