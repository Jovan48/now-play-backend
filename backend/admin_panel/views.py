"""
admin_panel/views.py

All views in this module:
  1. Require IsStaffUser permission (authenticated + is_staff=True).
  2. Use _get_model() to lazily resolve cross-app models so the module
     imports cleanly before the other teams define their models.
  3. Call _log() after every state-changing action to write an AuditLog entry.
  4. Return HTTP 503 with a descriptive message when a dependency model is
     not yet migrated, rather than crashing with an ImportError.
"""

import os

from django.apps import apps
from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta

from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AuditLog
from .permissions import IsStaffUser
from .serializers import (
    AdminCreatorSerializer,
    AdminSongSerializer,
    AdminAlbumSerializer,
    AuditLogSerializer,
    DashboardStatsSerializer,
    TopSongSerializer,
)


# ── Internal utilities ────────────────────────────────────────────────────────

def _get_model(app_label, model_name):
    """
    Safely resolve a model from a sibling app.
    Returns the model class, or None if it has not been registered yet
    (i.e. the owning app hasn't defined or migrated it).
    """
    try:
        return apps.get_model(app_label, model_name)
    except LookupError:
        return None


def _model_unavailable(model_name):
    """Standard 503 response when a cross-app model is not yet available."""
    return Response(
        {
            "detail": (
                f"'{model_name}' models are not yet available. "
                "The owning app has not been migrated yet."
            )
        },
        status=status.HTTP_503_SERVICE_UNAVAILABLE,
    )


def _log(request, action, target_model, target_id, detail=None):
    """
    Create an immutable AuditLog entry.
    Called after every admin action that modifies data.
    """
    AuditLog.objects.create(
        admin=request.user,
        action=action,
        target_model=target_model,
        target_id=target_id,
        detail=detail or {},
    )


class StandardPagination(PageNumberPagination):
    """20 results per page; client may request up to 100 via ?page_size=."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# ── Dashboard ─────────────────────────────────────────────────────────────────

class DashboardStatsView(APIView):
    """
    GET /api/admin/dashboard/

    Returns a snapshot of platform-wide metrics.  Counts that depend on models
    from other apps gracefully fall back to 0 if those models don't exist yet.
    The `models_status` field tells the frontend which sections are live.
    """
    permission_classes = [IsStaffUser]

    def get(self, request):
        User      = get_user_model()
        Song      = _get_model('music',     'Song')
        Album     = _get_model('music',     'Album')
        PlayEvent = _get_model('analytics', 'PlayEvent')

        # Total non-staff users = creators
        total_creators = User.objects.filter(is_staff=False).count()

        total_songs  = Song.objects.count()  if Song  else 0
        total_albums = Album.objects.count() if Album else 0

        # Pending songs only meaningful if Song has a 'status' field
        pending_songs = 0
        if Song and hasattr(Song, 'status'):
            pending_songs = Song.objects.filter(status='pending').count()

        # Plays in the last 7 days
        plays_this_week = 0
        if PlayEvent and hasattr(PlayEvent, 'played_at'):
            week_ago = timezone.now() - timedelta(days=7)
            plays_this_week = PlayEvent.objects.filter(
                played_at__gte=week_ago
            ).count()

        data = {
            'total_creators':  total_creators,
            'total_songs':     total_songs,
            'total_albums':    total_albums,
            'pending_songs':   pending_songs,
            'plays_this_week': plays_this_week,
            'models_status': {
                'accounts':  True,          # Always available (built-in User)
                'music':     Song  is not None,
                'analytics': PlayEvent is not None,
            },
        }
        return Response(DashboardStatsSerializer(data).data)


# ── Creator Management ────────────────────────────────────────────────────────

class CreatorListView(APIView):
    """
    GET /api/admin/creators/

    Query params:
      search       — username or email substring match
      is_verified  — 'true' | 'false'  (only if field exists on User model)
      is_suspended — 'true' | 'false'  (only if field exists on User model)
    """
    permission_classes = [IsStaffUser]

    def get(self, request):
        User = get_user_model()
        qs   = User.objects.filter(is_staff=False).order_by('-date_joined')

        if search := request.query_params.get('search'):
            query = Q(email__icontains=search)
            try:
                User._meta.get_field('username')
                query |= Q(username__icontains=search)
            except Exception:
                pass
            try:
                User._meta.get_field('stage_name')
                query |= Q(stage_name__icontains=search)
            except Exception:
                pass
            try:
                User._meta.get_field('full_name')
                query |= Q(full_name__icontains=search)
            except Exception:
                pass
            qs = qs.filter(query)

        # Optionally filter on custom fields if the accounts team has added them
        for flag in ('is_verified', 'is_suspended'):
            raw = request.query_params.get(flag)
            if raw is not None and hasattr(User, flag):
                qs = qs.filter(**{flag: raw.lower() == 'true'})

        paginator = StandardPagination()
        page      = paginator.paginate_queryset(qs, request)
        serializer = AdminCreatorSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class CreatorDetailView(APIView):
    """
    GET    /api/admin/creators/<pk>/  — Full creator detail
    DELETE /api/admin/creators/<pk>/  — Hard-delete the account
    """
    permission_classes = [IsStaffUser]

    def _get_creator(self, pk):
        User = get_user_model()
        try:
            return User.objects.get(pk=pk, is_staff=False)
        except User.DoesNotExist:
            return None

    def get(self, request, pk):
        creator = self._get_creator(pk)
        if creator is None:
            return Response(
                {'detail': 'Creator not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(AdminCreatorSerializer(creator).data)

    def delete(self, request, pk):
        creator = self._get_creator(pk)
        if creator is None:
            return Response(
                {'detail': 'Creator not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        _log(request, 'DELETE_CREATOR', 'CreatorUser', pk,
             {'username': getattr(creator, 'username', None) or creator.email, 'email': creator.email})
        creator.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CreatorVerifyView(APIView):
    """
    PATCH /api/admin/creators/<pk>/verify/

    Toggles the `is_verified` flag.  Returns 503 if the accounts team
    hasn't added the field yet.
    """
    permission_classes = [IsStaffUser]

    def patch(self, request, pk):
        User = get_user_model()
        try:
            creator = User.objects.get(pk=pk, is_staff=False)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Creator not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not hasattr(creator, 'is_verified'):
            return Response(
                {'detail': "'is_verified' is not yet defined on the User model."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        creator.is_verified = not creator.is_verified
        creator.save(update_fields=['is_verified'])

        action = 'VERIFY_CREATOR' if creator.is_verified else 'UNVERIFY_CREATOR'
        _log(request, action, 'CreatorUser', pk, {'is_verified': creator.is_verified})
        return Response({'id': pk, 'is_verified': creator.is_verified})


class CreatorSuspendView(APIView):
    """
    PATCH /api/admin/creators/<pk>/suspend/

    Toggles the `is_suspended` flag.  Returns 503 if the accounts team
    hasn't added the field yet.
    """
    permission_classes = [IsStaffUser]

    def patch(self, request, pk):
        User = get_user_model()
        try:
            creator = User.objects.get(pk=pk, is_staff=False)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Creator not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not hasattr(creator, 'is_suspended'):
            return Response(
                {'detail': "'is_suspended' is not yet defined on the User model."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        creator.is_suspended = not creator.is_suspended
        creator.save(update_fields=['is_suspended'])

        action = 'SUSPEND_CREATOR' if creator.is_suspended else 'UNSUSPEND_CREATOR'
        _log(request, action, 'CreatorUser', pk, {'is_suspended': creator.is_suspended})
        return Response({'id': pk, 'is_suspended': creator.is_suspended})


# ── Song Management ───────────────────────────────────────────────────────────

class SongListView(APIView):
    """
    GET /api/admin/songs/

    Query params:
      status  — pending | approved | rejected
      creator — creator PK
      genre   — genre PK
      search  — title substring
    """
    permission_classes = [IsStaffUser]

    def get(self, request):
        Song = _get_model('music', 'Song')
        if Song is None:
            return _model_unavailable('Song')

        select_fields = []
        prefetch_fields = []
        if hasattr(Song, 'artist'):
            select_fields.append('artist')
            Artist = _get_model('music', 'Artist')
            if Artist and hasattr(Artist, 'created_by'):
                select_fields.append('artist__created_by')
        if hasattr(Song, 'album'):
            select_fields.append('album')
        if hasattr(Song, 'creator'):
            select_fields.append('creator')
        if hasattr(Song, 'genre'):
            select_fields.append('genre')
        if hasattr(Song, 'genres'):
            prefetch_fields.append('genres')

        qs = Song.objects.select_related(*select_fields)
        if prefetch_fields:
            qs = qs.prefetch_related(*prefetch_fields)

        # Dynamic ordering: uploaded_at if available, else pk
        order_field = 'uploaded_at' if hasattr(Song, 'uploaded_at') else '-pk'
        qs = qs.order_by(f'-{order_field}') if order_field != '-pk' else qs.order_by(order_field)

        if status_f := request.query_params.get('status'):
            if hasattr(Song, 'status'):
                qs = qs.filter(status=status_f)
        if creator_id := request.query_params.get('creator'):
            if hasattr(Song, 'creator'):
                qs = qs.filter(creator_id=creator_id)
            elif hasattr(Song, 'artist'):
                qs = qs.filter(artist__created_by_id=creator_id)
        if genre_id := request.query_params.get('genre'):
            if hasattr(Song, 'genre'):
                qs = qs.filter(genre_id=genre_id)
            elif hasattr(Song, 'genres'):
                qs = qs.filter(genres__id=genre_id)
        if search := request.query_params.get('search'):
            qs = qs.filter(title__icontains=search)

        paginator  = StandardPagination()
        page       = paginator.paginate_queryset(qs, request)
        serializer = AdminSongSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class SongDetailView(APIView):
    """
    GET    /api/admin/songs/<pk>/
    DELETE /api/admin/songs/<pk>/  — Deletes the DB record and audio file on disk
    """
    permission_classes = [IsStaffUser]

    def _get_song(self, pk):
        Song = _get_model('music', 'Song')
        if Song is None:
            return None, True   # (song_obj, model_missing)
        try:
            select_fields = []
            prefetch_fields = []
            if hasattr(Song, 'artist'):
                select_fields.append('artist')
                Artist = _get_model('music', 'Artist')
                if Artist and hasattr(Artist, 'created_by'):
                    select_fields.append('artist__created_by')
            if hasattr(Song, 'album'):
                select_fields.append('album')
            if hasattr(Song, 'creator'):
                select_fields.append('creator')
            if hasattr(Song, 'genre'):
                select_fields.append('genre')
            if hasattr(Song, 'genres'):
                prefetch_fields.append('genres')

            qs = Song.objects.select_related(*select_fields)
            if prefetch_fields:
                qs = qs.prefetch_related(*prefetch_fields)
            return qs.get(pk=pk), False
        except Song.DoesNotExist:
            return None, False

    def get(self, request, pk):
        song, missing = self._get_song(pk)
        if missing:
            return _model_unavailable('Song')
        if song is None:
            return Response({'detail': 'Song not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(AdminSongSerializer(song).data)

    def delete(self, request, pk):
        song, missing = self._get_song(pk)
        if missing:
            return _model_unavailable('Song')
        if song is None:
            return Response({'detail': 'Song not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Attempt to remove the audio file from disk before deleting the record
        audio_field = getattr(song, 'audio_file', None)
        if audio_field:
            try:
                file_path = audio_field.path
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except (ValueError, OSError):
                # File path unavailable or already deleted — safe to continue
                pass

        _log(request, 'DELETE_SONG', 'Song', pk, {'title': song.title})
        song.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SongApproveView(APIView):
    """PATCH /api/admin/songs/<pk>/approve/"""
    permission_classes = [IsStaffUser]

    def patch(self, request, pk):
        Song = _get_model('music', 'Song')
        if Song is None:
            return _model_unavailable('Song')
        try:
            song = Song.objects.get(pk=pk)
        except Song.DoesNotExist:
            return Response({'detail': 'Song not found.'}, status=status.HTTP_404_NOT_FOUND)

        song.status = 'approved'
        song.save(update_fields=['status'])
        _log(request, 'APPROVE_SONG', 'Song', pk, {'title': song.title})
        return Response({'id': pk, 'status': 'approved'})


class SongRejectView(APIView):
    """
    PATCH /api/admin/songs/<pk>/reject/

    Optional body: { "reason": "..." }
    """
    permission_classes = [IsStaffUser]

    def patch(self, request, pk):
        Song = _get_model('music', 'Song')
        if Song is None:
            return _model_unavailable('Song')
        try:
            song = Song.objects.get(pk=pk)
        except Song.DoesNotExist:
            return Response({'detail': 'Song not found.'}, status=status.HTTP_404_NOT_FOUND)

        reason = request.data.get('reason', '')
        song.status = 'rejected'
        song.save(update_fields=['status'])
        _log(request, 'REJECT_SONG', 'Song', pk, {'title': song.title, 'reason': reason})
        return Response({'id': pk, 'status': 'rejected', 'reason': reason})


# ── Album Management ──────────────────────────────────────────────────────────

class AlbumListView(APIView):
    """
    GET /api/admin/albums/

    Query params:
      search — title substring
    """
    permission_classes = [IsStaffUser]

    def get(self, request):
        Album = _get_model('music', 'Album')
        if Album is None:
            return _model_unavailable('Album')

        qs = Album.objects.select_related('creator', 'artist')

        # Order by release_date if the field exists, else by pk desc
        if hasattr(Album, 'release_date'):
            qs = qs.order_by('-release_date')
        else:
            qs = qs.order_by('-pk')

        if search := request.query_params.get('search'):
            qs = qs.filter(title__icontains=search)

        paginator  = StandardPagination()
        page       = paginator.paginate_queryset(qs, request)
        serializer = AdminAlbumSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class AlbumDetailView(APIView):
    """
    GET    /api/admin/albums/<pk>/
    DELETE /api/admin/albums/<pk>/  — Cascades to child songs per DB constraints
    """
    permission_classes = [IsStaffUser]

    def _get_album(self, pk):
        Album = _get_model('music', 'Album')
        if Album is None:
            return None, True
        try:
            return Album.objects.select_related('creator', 'artist').get(pk=pk), False
        except Album.DoesNotExist:
            return None, False

    def get(self, request, pk):
        album, missing = self._get_album(pk)
        if missing:
            return _model_unavailable('Album')
        if album is None:
            return Response({'detail': 'Album not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(AdminAlbumSerializer(album).data)

    def delete(self, request, pk):
        album, missing = self._get_album(pk)
        if missing:
            return _model_unavailable('Album')
        if album is None:
            return Response({'detail': 'Album not found.'}, status=status.HTTP_404_NOT_FOUND)

        _log(request, 'DELETE_ALBUM', 'Album', pk, {'title': album.title})
        album.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Analytics Overview ────────────────────────────────────────────────────────

class AnalyticsOverviewView(APIView):
    """
    GET /api/admin/analytics/overview/

    Returns three datasets:
      - top_songs       : top 10 songs by total play count
      - plays_per_day   : daily play counts for the last 30 days
      - plays_by_genre  : aggregate plays grouped by genre name
    """
    permission_classes = [IsStaffUser]

    def get(self, request):
        PlayEvent = _get_model('analytics', 'PlayEvent')
        if PlayEvent is None:
            return _model_unavailable('PlayEvent')

        SongStats = _get_model('analytics', 'SongStats')
        Song      = _get_model('music',     'Song')

        # ── Top 10 songs ──────────────────────────────────────────────────────
        top_songs = []
        if SongStats and Song:
            try:
                top_qs = (
                    SongStats.objects
                    .select_related('song', 'song__creator')
                    .order_by('-total_plays')[:10]
                )
                for stat in top_qs:
                    creator = getattr(stat.song, 'creator', None)
                    top_songs.append({
                        'id':               stat.song.id,
                        'title':            stat.song.title,
                        'total_plays':      stat.total_plays,
                        'creator_username': getattr(creator, 'username', None),
                    })
            except Exception:
                top_songs = []

        # ── Plays per day (last 30 days) ──────────────────────────────────────
        plays_per_day = []
        if hasattr(PlayEvent, 'played_at'):
            try:
                thirty_ago = timezone.now() - timedelta(days=30)
                plays_per_day = list(
                    PlayEvent.objects
                    .filter(played_at__gte=thirty_ago)
                    .annotate(date=TruncDate('played_at'))
                    .values('date')
                    .annotate(count=Count('id'))
                    .order_by('date')
                )
            except Exception:
                plays_per_day = []

        # ── Plays by genre ────────────────────────────────────────────────────
        plays_by_genre = []
        if Song and hasattr(Song, 'genre') and SongStats:
            try:
                plays_by_genre = list(
                    Song.objects
                    .values('genre__name')
                    .annotate(total_plays=Sum('stats__total_plays'))
                    .order_by('-total_plays')
                )
            except Exception:
                plays_by_genre = []

        return Response({
            'top_songs': TopSongSerializer(top_songs, many=True).data,
            'plays_per_day': [
                {'date': str(entry['date']), 'count': entry['count']}
                for entry in plays_per_day
            ],
            'plays_by_genre': [
                {
                    'genre':       entry.get('genre__name') or 'Unknown',
                    'total_plays': entry.get('total_plays') or 0,
                }
                for entry in plays_by_genre
            ],
        })


# ── Audit Log ─────────────────────────────────────────────────────────────────

class AuditLogListView(APIView):
    """
    GET /api/admin/audit-log/

    Read-only, paginated list of all admin actions.

    Query params:
      action       — filter by exact action code (e.g. APPROVE_SONG)
      admin        — filter by admin user PK
      target_model — filter by model name (case-insensitive)
    """
    permission_classes = [IsStaffUser]

    def get(self, request):
        qs = AuditLog.objects.select_related('admin').order_by('-timestamp')

        if action := request.query_params.get('action'):
            qs = qs.filter(action=action)
        if admin_id := request.query_params.get('admin'):
            qs = qs.filter(admin_id=admin_id)
        if target_model := request.query_params.get('target_model'):
            qs = qs.filter(target_model__iexact=target_model)

        paginator  = StandardPagination()
        page       = paginator.paginate_queryset(qs, request)
        serializer = AuditLogSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
