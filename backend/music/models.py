from django.conf import settings
from django.db import models


def artist_photo_upload_path(instance, filename):
    return f'artists/{instance.name[:50]}/photos/{filename}'


def album_cover_upload_path(instance, filename):
    return f'albums/{instance.artist.name[:50]}/covers/{filename}'


def song_audio_upload_path(instance, filename):
    return f'songs/{instance.artist.name[:50]}/{filename}'


class Genre(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Artist(models.Model):
    name = models.CharField(max_length=200, unique=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to=artist_photo_upload_path, null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='artists',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Album(models.Model):
    title = models.CharField(max_length=255)
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        related_name='albums',
    )
    cover_image = models.ImageField(upload_to=album_cover_upload_path, null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-release_date', 'title']
        unique_together = ('title', 'artist')

    def __str__(self):
        return f'{self.title} — {self.artist.name}'


class Song(models.Model):
    title = models.CharField(max_length=255)
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        related_name='songs',
    )
    album = models.ForeignKey(
        Album,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='songs',
    )
    audio_file = models.FileField(upload_to=song_audio_upload_path)
    duration = models.PositiveIntegerField(null=True, blank=True)
    track_number = models.PositiveIntegerField(null=True, blank=True)
    plays = models.PositiveIntegerField(default=0)
    release_date = models.DateField(null=True, blank=True)
    genres = models.ManyToManyField(Genre, blank=True, related_name='songs')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['track_number', 'title']
        unique_together = ('title', 'artist', 'album')

    def __str__(self):
        return f'{self.title} — {self.artist.name}'
