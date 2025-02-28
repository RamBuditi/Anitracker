from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
import aiohttp
from .utils import fetch_anime_details, parse_duration_to_minutes
import requests
import re

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    bio = models.TextField(blank=True)
    favorite_anime_ids = models.JSONField(default=list, blank=True)

    def get_jikan_anime_details(self, anime_id):
        """
        Fetches anime details from the Jikan API synchronously.
        """
        url = f"https://api.jikan.moe/v4/anime/{anime_id}"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            data = response.json()
            return data['data']
        except requests.exceptions.RequestException as e:
            print(f"Error fetching anime details from Jikan API: {e}")
            return None

    def get_watch_stats(self):
        """
        Calculate and return user's anime watching statistics
        """
        # Get all entries for the user first
        entries = self.animeentry_set.all()
        
        # Filter entries by status
        watched = entries.filter(status='completed')
        watching = entries.filter(status='watching')
        planned = entries.filter(status='plan_to_watch')
        dropped = entries.filter(status='dropped')
        
        # Calculate total watch time in minutes
        total_time = 0
        # Include time from completed shows
        for entry in watched:
            if entry.anime_duration and entry.episodes_watched:
                total_time += entry.anime_duration * entry.episodes_watched
        
        # Add time from currently watching shows
        for entry in watching:
            if entry.anime_duration and entry.episodes_watched:
                total_time += entry.anime_duration * entry.episodes_watched
        
        # Convert minutes to days (rounded to 2 decimal places)
        total_days = round(total_time / (24 * 60), 2)
        
        return {
            'watched_count': watched.count(),
            'total_days': total_days,
            'watching_count': watching.count(),
            'planned_count': planned.count(),
            'dropped_count': dropped.count()
        }

        
    def __str__(self):
        return self.user.username

class AnimeEntry(models.Model):
    STATUS_CHOICES = [
        ('watching', 'Currently Watching'),
        ('completed', 'Completed'),
        ('plan_to_watch', 'Plan to Watch'),
        ('dropped', 'Dropped')
    ]

    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    anime_id = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    rating = models.IntegerField(null=True, blank=True, choices=[(i, i) for i in range(1, 11)])
    episodes_watched = models.IntegerField(default=0)
    anime_duration = models.FloatField(default=0.0)  
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user_profile', 'anime_id']

    def save(self, *args, **kwargs):
        """
        Override save to fetch anime duration from Jikan API if not already set.
        """
        if not self.anime_duration and self.anime_id:
            anime_details = self.user_profile.get_jikan_anime_details(self.anime_id)
            if anime_details:
                duration_str = anime_details.get('duration', '0 mins per ep') # Default value if not found

                # Extract duration in minutes using regex
                match = re.search(r'(\d+)\s*min', duration_str)
                if match:
                    self.anime_duration = float(match.group(1))

        super().save(*args, **kwargs)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance, name=instance.username)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

class AnimeReview(models.Model):
    RECOMMENDATION_CHOICES = [
        ('recommends', 'Recommends'),
        ('mixed', 'Mixed Feelings'),
        ('not_recommended', 'Does Not Recommend')
    ]
    
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    anime_id = models.IntegerField()
    review_text = models.TextField()
    recommendation = models.CharField(max_length=20, choices=RECOMMENDATION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Link to the anime entry to get rating and episodes watched
    anime_entry = models.OneToOneField(
        AnimeEntry, 
        on_delete=models.CASCADE,
        null=True, 
        blank=True
    )
    
    class Meta:
        unique_together = ['user_profile', 'anime_id']
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user_profile.user.username} for Anime {self.anime_id}"