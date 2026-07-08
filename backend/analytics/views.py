"""
Analytics views — Now Play for Creators
========================================
All endpoints require JWT authentication unless otherwise noted.

Endpoints
---------
POST   /api/analytics/stream/                  Log a stream/play event
POST   /api/analytics/follow/                  Log a follow/unfollow event
GET    /api/analytics/artist/summary/          Artist dashboard summary
GET    /api/analytics/artist/top-songs/        Artist's top songs by play count
GET    /api/analytics/artist/listening-history/ Recent plays on artist's songs
GET    /api/analytics/artist/geographic/       Play counts by country
GET    /api/analytics/artist/follower-growth/  Daily follower growth
GET    /api/analytics/top-charts/              Platform-wide top songs (public)
"""

from datetime import timedelta, date

from django.db.models import (
    Count, Q, DateField, IntegerField
)
from django.db.models.functions import TruncDate
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import StreamEvent, FollowEvent
from .serializers import (
    ArtistSummarySerializer,
    FollowEventCreateSerializer,
    FollowerGrowthSerializer,
    GeographicSerializer,
    StreamEventCreateSerializer,
    StreamEventSerializer,
    TopSongSerializer,
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _parse_period(request) -> int:
    """
    Read ?period=7d|30d|90d|all from query params.
    Returns the number of days, or None for 'all time'.
    """
    period = request.query_params.get('period', '30d')
    mapping = {'7d': 7, '30d': 30, '90d': 90, 'all': None}
    return mapping.get(period, 30)


def _since(days: int | None):
    """Return the cutoff datetime, or None for all-time queries."""
    if days is None:
        return None
    return timezone.now() - timedelta(days=days)


# ---------------------------------------------------------------------------
# Stream / Follow event logging
# ---------------------------------------------------------------------------

class LogStreamView(APIView):
    """
    POST /api/analytics/stream/
    Log that the authenticated user (or an anonymous visitor) played a song.
    The frontend should call this as soon as a song starts playing.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = StreamEventCreateSerializer(
            data=request.data,
            context={'request': request},
        )
        if serializer.is_valid():
            event = serializer.save()
            return Response(
                {'id': event.id, 'detail': 'Stream logged.'},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogFollowView(APIView):
    """
    POST /api/analytics/follow/
    Record a follow or unfollow action for an artist.
    Body: { "artist": <user_id>, "action": "follow" | "unfollow" }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FollowEventCreateSerializer(
            data=request.data,
            context={'request': request},
        )
        if serializer.is_valid():
            event = serializer.save()
            return Response(
                {'id': event.id, 'detail': f'{event.action.capitalize()} recorded.'},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------
# Artist dashboard views
# ---------------------------------------------------------------------------

class ArtistSummaryView(APIView):
    """
    GET /api/analytics/artist/summary/?period=30d
    Returns aggregate stats for the requesting artist's songs.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        days = _parse_period(request)
        cutoff = _since(days)
        artist = request.user

        stream_qs = StreamEvent.objects.filter(song__artist=artist)
        if cutoff:
            stream_qs = stream_qs.filter(played_at__gte=cutoff)

        total_plays = stream_qs.count()
        unique_listeners = stream_qs.exclude(user=None).values('user').distinct().count()
        total_followers = FollowEvent.objects.filter(
            artist=artist, action=FollowEvent.FOLLOW
        ).count() - FollowEvent.objects.filter(
            artist=artist, action=FollowEvent.UNFOLLOW
        ).count()

        data = {
            'total_plays': total_plays,
            'unique_listeners': unique_listeners,
            'total_followers': max(total_followers, 0),
            'period_days': days if days is not None else -1,
        }
        serializer = ArtistSummarySerializer(data)
        return Response(serializer.data)


class ArtistTopSongsView(APIView):
    """
    GET /api/analytics/artist/top-songs/?period=30d&limit=10
    Returns the requesting artist's songs ranked by play count.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        days = _parse_period(request)
        cutoff = _since(days)
        limit = min(int(request.query_params.get('limit', 10)), 50)
        artist = request.user

        qs = (
            StreamEvent.objects
            .filter(song__artist=artist)
        )
        if cutoff:
            qs = qs.filter(played_at__gte=cutoff)

        top = (
            qs.values('song__id', 'song__title')
            .annotate(play_count=Count('id'))
            .order_by('-play_count')[:limit]
        )

        data = [
            {
                'song_id': row['song__id'],
                'song_title': row['song__title'],
                'play_count': row['play_count'],
            }
            for row in top
        ]
        serializer = TopSongSerializer(data, many=True)
        return Response(serializer.data)


class ArtistListeningHistoryView(APIView):
    """
    GET /api/analytics/artist/listening-history/?period=30d&limit=50
    Returns the most recent StreamEvents for the requesting artist's songs.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        days = _parse_period(request)
        cutoff = _since(days)
        limit = min(int(request.query_params.get('limit', 50)), 200)
        artist = request.user

        qs = StreamEvent.objects.filter(song__artist=artist).select_related('user', 'song')
        if cutoff:
            qs = qs.filter(played_at__gte=cutoff)

        events = qs[:limit]
        serializer = StreamEventSerializer(events, many=True)
        return Response(serializer.data)


class ArtistGeographicView(APIView):
    """
    GET /api/analytics/artist/geographic/?period=30d
    Returns play counts grouped by country_code for the requesting artist's songs.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        days = _parse_period(request)
        cutoff = _since(days)
        artist = request.user

        qs = StreamEvent.objects.filter(song__artist=artist).exclude(country_code='')
        if cutoff:
            qs = qs.filter(played_at__gte=cutoff)

        breakdown = (
            qs.values('country_code')
            .annotate(play_count=Count('id'))
            .order_by('-play_count')
        )

        data = [
            {'country_code': row['country_code'], 'play_count': row['play_count']}
            for row in breakdown
        ]
        serializer = GeographicSerializer(data, many=True)
        return Response(serializer.data)


class ArtistFollowerGrowthView(APIView):
    """
    GET /api/analytics/artist/follower-growth/?period=30d
    Returns daily follower/unfollow counts and net change for the requesting artist.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        days = _parse_period(request)
        cutoff = _since(days)
        artist = request.user

        qs = FollowEvent.objects.filter(artist=artist)
        if cutoff:
            qs = qs.filter(timestamp__gte=cutoff)

        # Annotate by date and action
        follows_by_day = (
            qs.filter(action=FollowEvent.FOLLOW)
            .annotate(date=TruncDate('timestamp'))
            .values('date')
            .annotate(follows=Count('id'))
        )
        unfollows_by_day = (
            qs.filter(action=FollowEvent.UNFOLLOW)
            .annotate(date=TruncDate('timestamp'))
            .values('date')
            .annotate(unfollows=Count('id'))
        )

        # Merge into a single dict keyed by date
        growth: dict[date, dict] = {}
        for row in follows_by_day:
            growth.setdefault(row['date'], {'follows': 0, 'unfollows': 0})
            growth[row['date']]['follows'] = row['follows']
        for row in unfollows_by_day:
            growth.setdefault(row['date'], {'follows': 0, 'unfollows': 0})
            growth[row['date']]['unfollows'] = row['unfollows']

        data = sorted(
            [
                {
                    'date': d,
                    'follows': v['follows'],
                    'unfollows': v['unfollows'],
                    'net': v['follows'] - v['unfollows'],
                }
                for d, v in growth.items()
            ],
            key=lambda x: x['date'],
        )
        serializer = FollowerGrowthSerializer(data, many=True)
        return Response(serializer.data)


# ---------------------------------------------------------------------------
# Public platform-wide views
# ---------------------------------------------------------------------------

class TopChartsView(APIView):
    """
    GET /api/analytics/top-charts/?period=7d&limit=20
    Platform-wide top songs by total play count. No authentication required.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        days = _parse_period(request)
        cutoff = _since(days)
        limit = min(int(request.query_params.get('limit', 20)), 100)

        qs = StreamEvent.objects.all()
        if cutoff:
            qs = qs.filter(played_at__gte=cutoff)

        top = (
            qs.values('song__id', 'song__title')
            .annotate(play_count=Count('id'))
            .order_by('-play_count')[:limit]
        )

        data = [
            {
                'song_id': row['song__id'],
                'song_title': row['song__title'],
                'play_count': row['play_count'],
            }
            for row in top
        ]
        serializer = TopSongSerializer(data, many=True)
        return Response(serializer.data)
