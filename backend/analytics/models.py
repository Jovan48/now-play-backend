from django.conf import settings
from django.db import models


class PlayEvent(models.Model):
    """
    One row per song play — the raw event log everything else is
    computed from. Deliberately simple: cheap to write on every play,
    and flexible enough to aggregate however we need later.
    """

    SOURCE_CHOICES = [
        ('direct', 'Direct / search'),
        ('playlist', 'Playlist'),
        ('artist_page', 'Artist page'),
        ('album_page', 'Album page'),
        ('recommendation', 'Recommended'),
        ('other', 'Other'),
    ]

    song = models.ForeignKey(
        'music.Song',
        on_delete=models.CASCADE,
        related_name='play_events',
    )
    listener = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='play_events',
    )
    played_at = models.DateTimeField(auto_now_add=True)

    # Optional — populate once the player can report them.
    # Nullable so this works today even without full player instrumentation.
    seconds_listened = models.PositiveIntegerField(null=True, blank=True)
    completion_percentage = models.FloatField(null=True, blank=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='other')

    class Meta:
        ordering = ['-played_at']
        indexes = [
            models.Index(fields=['song', 'played_at']),
            models.Index(fields=['listener', 'played_at']),
        ]

    def __str__(self):
        return f'{self.song.title} played at {self.played_at}'