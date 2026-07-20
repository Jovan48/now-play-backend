from django.db.models import F
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from . import models, permissions, serializers, utils


class SongViewSet(viewsets.ModelViewSet):
    queryset = models.Song.objects.select_related('artist', 'album').prefetch_related('genres').all()
    serializer_class = serializers.SongSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, permissions.IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        artist = serializer.validated_data['artist']
        if artist.created_by is not None and artist.created_by != self.request.user:
            raise PermissionDenied('Cannot add songs to an artist you do not own.')

        song = serializer.save()

        if song.artist.created_by is None and self.request.user.is_authenticated:
            song.artist.created_by = self.request.user
            song.artist.save(update_fields=['created_by'])

        return song
    @action(detail=True, methods=['post'])
    def play(self, request, pk=None):
        song = self.get_object()
        song.plays = F('plays') + 1
        song.save(update_fields=['plays'])
        song.refresh_from_db()

        # Record a detailed event alongside the simple counter.
        # seconds_listened / completion_percentage are optional — send them
        # once your player can report how far a listener got.
        from analytics.models import PlayEvent
        PlayEvent.objects.create(
            song=song,
            listener=request.user if request.user.is_authenticated else None,
            seconds_listened=request.data.get('seconds_listened'),
            completion_percentage=request.data.get('completion_percentage'),
            source=request.data.get('source', 'other'),
        )

        return Response({'id': song.id, 'plays': song.plays}, status=status.HTTP_200_OK)

class AlbumViewSet(viewsets.ModelViewSet):
    queryset = models.Album.objects.select_related('artist').prefetch_related('songs').all()
    serializer_class = serializers.AlbumSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, permissions.IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        artist = serializer.validated_data['artist']
        if artist.created_by is not None and artist.created_by != self.request.user:
            raise PermissionDenied('Cannot create an album for an artist you do not own.')

        album = serializer.save()
        if album.artist.created_by is None and self.request.user.is_authenticated:
            album.artist.created_by = self.request.user
            album.artist.save(update_fields=['created_by'])
        return album


class ArtistViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Artist.objects.prefetch_related('albums', 'songs').all()
    serializer_class = serializers.ArtistSerializer
    permission_classes = [AllowAny]


class SearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        songs = models.Song.objects.filter(title__icontains=query)
        albums = models.Album.objects.filter(title__icontains=query)
        artists = models.Artist.objects.filter(name__icontains=query)

        return Response({
            'songs': serializers.SongSerializer(songs, many=True, context={'request': request}).data,
            'albums': serializers.AlbumSerializer(albums, many=True, context={'request': request}).data,
            'artists': serializers.ArtistSerializer(artists, many=True, context={'request': request}).data,
        })
