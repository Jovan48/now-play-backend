from rest_framework import serializers
from .models import StreamEvent, FollowEvent


# ---------------------------------------------------------------------------
# Input serializers (for POST endpoints)
# ---------------------------------------------------------------------------

class StreamEventCreateSerializer(serializers.ModelSerializer):
    """Validates + creates a StreamEvent. The user is set from the request."""

    class Meta:
        model = StreamEvent
        fields = ['song', 'duration_seconds', 'country_code']

    def create(self, validated_data):
        request = self.context['request']
        user = request.user if request.user.is_authenticated else None
        return StreamEvent.objects.create(user=user, **validated_data)


class FollowEventCreateSerializer(serializers.ModelSerializer):
    """Validates + creates a FollowEvent. The follower is set from the request."""

    class Meta:
        model = FollowEvent
        fields = ['artist', 'action']

    def validate(self, attrs):
        request = self.context['request']
        if attrs['artist'] == request.user:
            raise serializers.ValidationError("You cannot follow yourself.")
        return attrs

    def create(self, validated_data):
        follower = self.context['request'].user
        return FollowEvent.objects.create(follower=follower, **validated_data)


# ---------------------------------------------------------------------------
# Output / response serializers
# ---------------------------------------------------------------------------

class StreamEventSerializer(serializers.ModelSerializer):
    """Full representation of a stream event (used in listening history)."""
    song_title = serializers.CharField(source='song.title', read_only=True)
    listener_username = serializers.SerializerMethodField()

    def get_listener_username(self, obj):
        """Return username or 'anonymous' safely when user FK is None."""
        return obj.user.username if obj.user_id else 'anonymous'

    class Meta:
        model = StreamEvent
        fields = [
            'id',
            'song',
            'song_title',
            'listener_username',
            'played_at',
            'duration_seconds',
            'country_code',
        ]


class ArtistSummarySerializer(serializers.Serializer):
    """Response shape for the artist dashboard summary endpoint."""
    total_plays = serializers.IntegerField()
    unique_listeners = serializers.IntegerField()
    total_followers = serializers.IntegerField()
    period_days = serializers.IntegerField()


class TopSongSerializer(serializers.Serializer):
    """Response shape for top-songs and top-charts endpoints."""
    song_id = serializers.IntegerField()
    song_title = serializers.CharField()
    play_count = serializers.IntegerField()


class GeographicSerializer(serializers.Serializer):
    """Response shape for geographic breakdown."""
    country_code = serializers.CharField()
    play_count = serializers.IntegerField()


class FollowerGrowthSerializer(serializers.Serializer):
    """Response shape for daily follower growth."""
    date = serializers.DateField()
    follows = serializers.IntegerField()
    unfollows = serializers.IntegerField()
    net = serializers.IntegerField()
