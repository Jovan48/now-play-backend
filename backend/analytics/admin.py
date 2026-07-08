from django.contrib import admin
from .models import StreamEvent, FollowEvent


@admin.register(StreamEvent)
class StreamEventAdmin(admin.ModelAdmin):
    list_display = ['id', 'song', 'user', 'played_at', 'duration_seconds', 'country_code']
    list_filter = ['country_code', 'played_at']
    search_fields = ['song__title', 'user__username', 'country_code']
    readonly_fields = ['played_at']
    date_hierarchy = 'played_at'
    ordering = ['-played_at']


@admin.register(FollowEvent)
class FollowEventAdmin(admin.ModelAdmin):
    list_display = ['id', 'follower', 'artist', 'action', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['follower__username', 'artist__username']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
