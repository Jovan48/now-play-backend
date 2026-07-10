"""
admin_panel/serializers.py

All serializers in this module are written using plain `serializers.Serializer`
(not ModelSerializer) for cross-app models, so they remain importable even
before the accounts/music/analytics teams define their models.

`AuditLogSerializer` is a ModelSerializer because AuditLog is defined locally.
"""

from rest_framework import serializers
from .models import AuditLog


# ── Audit Log ─────────────────────────────────────────────────────────────────

class AuditLogSerializer(serializers.ModelSerializer):
    # Resolved from the FK relation; falls back gracefully if admin was deleted.
    admin_username = serializers.CharField(
        source='admin.email',
        read_only=True,
        default='(deleted)',
    )

    class Meta:
        model = AuditLog
        fields = [
            'id', 'admin_username', 'action',
            'target_model', 'target_id', 'detail', 'timestamp',
        ]
        read_only_fields = fields


# ── Dashboard ─────────────────────────────────────────────────────────────────

class DashboardStatsSerializer(serializers.Serializer):
    total_creators   = serializers.IntegerField()
    total_songs      = serializers.IntegerField()
    total_albums     = serializers.IntegerField()
    pending_songs    = serializers.IntegerField()
    plays_this_week  = serializers.IntegerField()
    # Boolean map showing which app's models are already defined.
    models_status    = serializers.DictField(child=serializers.BooleanField())


# ── Creator Management ────────────────────────────────────────────────────────

class AdminCreatorSerializer(serializers.Serializer):
    """
    Adapts to whatever fields the accounts team puts on their User model.
    Uses `getattr` with safe defaults so optional fields like `is_verified`
    and `is_suspended` don't break the endpoint if not yet defined.
    """

    id           = serializers.IntegerField()
    username     = serializers.EmailField(source='email')
    email        = serializers.EmailField()
    is_staff     = serializers.BooleanField()
    date_joined  = serializers.DateTimeField()

    # Extended fields — provided by accounts team's custom User model.
    display_name = serializers.SerializerMethodField()
    is_verified  = serializers.SerializerMethodField()
    is_suspended = serializers.SerializerMethodField()
    song_count   = serializers.SerializerMethodField()

    def get_display_name(self, obj):
        return getattr(obj, 'display_name', None) or obj.get_full_name() or obj.email

    def get_is_verified(self, obj):
        # Default False if the field doesn't exist yet.
        return getattr(obj, 'is_verified', False)

    def get_is_suspended(self, obj):
        return getattr(obj, 'is_suspended', False)

    def get_song_count(self, obj):
        """Count songs by this creator; returns null if music app not ready."""
        from django.apps import apps
        try:
            Song = apps.get_model('music', 'Song')
            # Fall back to checking artist__created_by if creator field doesn't exist
            if hasattr(Song, 'creator'):
                return Song.objects.filter(creator=obj).count()
            else:
                return Song.objects.filter(artist__created_by=obj).count()
        except LookupError:
            return None


# ── Song Management ───────────────────────────────────────────────────────────

class AdminSongSerializer(serializers.Serializer):
    """
    Flexible song representation.  All relational fields use SerializerMethodField
    with getattr so the serializer works even if the Song model schema changes.
    """

    id          = serializers.IntegerField()
    title       = serializers.CharField()
    status      = serializers.SerializerMethodField()
    source      = serializers.SerializerMethodField()
    file_size   = serializers.SerializerMethodField()
    duration    = serializers.SerializerMethodField()
    uploaded_at = serializers.SerializerMethodField()
    creator     = serializers.SerializerMethodField()
    genre       = serializers.SerializerMethodField()
    artist      = serializers.SerializerMethodField()
    album       = serializers.SerializerMethodField()

    def get_status(self, obj):
        return getattr(obj, 'status', None)

    def get_source(self, obj):
        return getattr(obj, 'source', None)

    def get_file_size(self, obj):
        return getattr(obj, 'file_size', None)

    def get_duration(self, obj):
        return getattr(obj, 'duration', None)

    def get_uploaded_at(self, obj):
        val = getattr(obj, 'uploaded_at', None)
        return val.isoformat() if val else None

    def get_creator(self, obj):
        creator = getattr(obj, 'creator', None)
        if not creator and hasattr(obj, 'artist') and obj.artist:
            creator = getattr(obj.artist, 'created_by', None)
        if creator:
            username = getattr(creator, 'username', None) or getattr(creator, 'email', '')
            return {'id': creator.id, 'username': username}
        return None

    def get_genre(self, obj):
        genre = getattr(obj, 'genre', None)
        if genre:
            return {'id': genre.id, 'name': genre.name}
        return None

    def get_artist(self, obj):
        artist = getattr(obj, 'artist', None)
        if artist:
            return {'id': artist.id, 'name': artist.name}
        return None

    def get_album(self, obj):
        album = getattr(obj, 'album', None)
        if album:
            return {'id': album.id, 'title': album.title}
        return None


# ── Album Management ──────────────────────────────────────────────────────────

class AdminAlbumSerializer(serializers.Serializer):
    id           = serializers.IntegerField()
    title        = serializers.CharField()
    release_date = serializers.SerializerMethodField()
    creator      = serializers.SerializerMethodField()
    artist       = serializers.SerializerMethodField()
    song_count   = serializers.SerializerMethodField()

    def get_release_date(self, obj):
        val = getattr(obj, 'release_date', None)
        return str(val) if val else None

    def get_creator(self, obj):
        creator = getattr(obj, 'creator', None)
        if not creator and hasattr(obj, 'artist') and obj.artist:
            creator = getattr(obj.artist, 'created_by', None)
        if creator:
            username = getattr(creator, 'username', None) or getattr(creator, 'email', '')
            return {'id': creator.id, 'username': username}
        return None

    def get_artist(self, obj):
        artist = getattr(obj, 'artist', None)
        if artist:
            return {'id': artist.id, 'name': artist.name}
        return None

    def get_song_count(self, obj):
        # Try common reverse manager names the music team might use.
        for attr in ('songs', 'song_set'):
            manager = getattr(obj, attr, None)
            if manager is not None:
                try:
                    return manager.count()
                except Exception:
                    pass
        return None


# ── Analytics ─────────────────────────────────────────────────────────────────

class TopSongSerializer(serializers.Serializer):
    id               = serializers.IntegerField()
    title            = serializers.CharField()
    total_plays      = serializers.IntegerField()
    creator_username = serializers.CharField(allow_null=True)
