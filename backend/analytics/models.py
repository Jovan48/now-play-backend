from django.db import models
from django.conf import settings


class StreamEvent(models.Model):
    """
    Records every time a user plays (streams) a song.
    This is the single source of truth for all play/stream analytics.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='stream_events',
        help_text='The listener (null = anonymous play)',
    )
    # ForeignKey to music.Song — uses string reference to stay decoupled
    song = models.ForeignKey(
        'music.Song',
        on_delete=models.CASCADE,
        related_name='stream_events',
        help_text='The song that was played',
    )
    played_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Timestamp when the play was logged',
    )
    duration_seconds = models.PositiveIntegerField(
        default=0,
        help_text='How many seconds of the song the user listened to',
    )
    country_code = models.CharField(
        max_length=2,
        blank=True,
        default='',
        help_text='ISO 3166-1 alpha-2 country code of the listener',
    )

    class Meta:
        ordering = ['-played_at']
        indexes = [
            # Fast lookups for per-song and per-artist dashboard queries
            models.Index(fields=['song', 'played_at'], name='analytics_song_played_idx'),
            models.Index(fields=['played_at'], name='analytics_played_at_idx'),
            models.Index(fields=['country_code'], name='analytics_country_idx'),
        ]

    def __str__(self):
        if self.user:
            user_label = getattr(self.user, 'username', None) or getattr(self.user, 'email', 'anonymous')
        else:
            user_label = 'anonymous'
        return f"{user_label} played {self.song_id} at {self.played_at:%Y-%m-%d %H:%M}"


class FollowEvent(models.Model):
    """
    Append-only log of follow/unfollow actions.
    Used to compute follower growth over time for an artist.
    """
    FOLLOW = 'follow'
    UNFOLLOW = 'unfollow'
    ACTION_CHOICES = [
        (FOLLOW, 'Follow'),
        (UNFOLLOW, 'Unfollow'),
    ]

    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='follow_events_made',
        help_text='The user who performed the follow/unfollow',
    )
    artist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='follow_events_received',
        help_text='The artist/creator being followed or unfollowed',
    )
    action = models.CharField(
        max_length=8,
        choices=ACTION_CHOICES,
        help_text='"follow" or "unfollow"',
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text='When the action occurred',
    )

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['artist', 'timestamp'], name='analytics_artist_follow_idx'),
        ]

    def __str__(self):
        follower_label = getattr(self.follower, 'username', None) or getattr(self.follower, 'email', 'unknown')
        artist_label = getattr(self.artist, 'username', None) or getattr(self.artist, 'email', 'unknown')
        return f"{follower_label} {self.action}ed {artist_label} at {self.timestamp:%Y-%m-%d %H:%M}"
