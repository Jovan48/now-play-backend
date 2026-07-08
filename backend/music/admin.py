from django.contrib import admin
from django.utils.html import format_html

from .models import Album, Artist, Genre, Song


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at', 'photo_preview')
    search_fields = ('name', 'bio')
    readonly_fields = ('photo_preview',)

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="60" height="60" style="object-fit: cover;"/>', obj.photo.url)
        return '-'

    photo_preview.short_description = 'Photo'


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'release_date', 'cover_preview')
    list_filter = ('artist', 'release_date')
    search_fields = ('title', 'artist__name')
    readonly_fields = ('cover_preview',)
    actions = ['delete_selected_albums_keep_songs']

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" width="80" height="80" style="object-fit: cover;"/>', obj.cover_image.url)
        return '-'

    cover_preview.short_description = 'Cover'

    def delete_selected_albums_keep_songs(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'Deleted {count} albums. Songs were retained with album set to null.')

    delete_selected_albums_keep_songs.short_description = 'Delete selected albums and keep songs'


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'album', 'plays', 'release_date')
    list_filter = ('artist', 'album', 'genres', 'release_date')
    search_fields = ('title', 'artist__name', 'album__title')
    actions = ['reset_play_counts']

    def reset_play_counts(self, request, queryset):
        updated = queryset.update(plays=0)
        self.message_user(request, f'Reset play count for {updated} song(s).')

    reset_play_counts.short_description = 'Reset play counts'
