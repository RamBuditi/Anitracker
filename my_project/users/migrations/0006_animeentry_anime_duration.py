# Generated by Django 4.2.17 on 2025-01-27 23:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_remove_animeentry_anime_duration'),
    ]

    operations = [
        migrations.AddField(
            model_name='animeentry',
            name='anime_duration',
            field=models.IntegerField(default=0),
        ),
    ]
