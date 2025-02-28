from django.contrib import admin
from .models import UserProfile, AnimeEntry

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'bio')
    search_fields = ('user__username', 'name')

@admin.register(AnimeEntry)
class AnimeEntryAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'anime_id', 'status', 'rating', 'episodes_watched')
    list_filter = ('status', 'rating')
    search_fields = ('user_profile__user__username', 'anime_id')