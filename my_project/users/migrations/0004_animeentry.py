# Generated by Django 4.2.17 on 2025-01-23 11:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_userprofile_favorite_anime_ids'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnimeEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('anime_id', models.IntegerField()),
                ('status', models.CharField(choices=[('watching', 'Currently Watching'), ('completed', 'Completed'), ('plan_to_watch', 'Plan to Watch'), ('dropped', 'Dropped')], max_length=20)),
                ('rating', models.IntegerField(blank=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)], null=True)),
                ('episodes_watched', models.IntegerField(default=0)),
                ('anime_duration', models.IntegerField(default=0)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('user_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.userprofile')),
            ],
            options={
                'unique_together': {('user_profile', 'anime_id')},
            },
        ),
    ]
