# Generated by Django 4.2.17 on 2025-01-28 00:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_animeentry_anime_duration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='animeentry',
            name='anime_duration',
            field=models.FloatField(default=0.0),
        ),
    ]
