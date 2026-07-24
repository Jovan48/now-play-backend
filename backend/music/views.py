from django.db.models import F
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from . import models, permissions, serializers, utils


class AlbumViewSet(viewsets.ModelViewSet):                                                                                                                
        queryset = models.Album.objects.select_related('artist').prefetch_related('songs').all()                                                              
        serializer_class = serializers.AlbumSerializer                                                                                                        
        permission_classes = [IsAuthenticatedOrReadOnly, permissions.IsOwnerOrReadOnly]                                                                       
                                                                                                                                                              
        def perform_create(self, serializer):                                                                                                                 
            artist = serializer.validated_data.get('artist')                                                                                                  
                                                                                                                                                              
            if not artist and self.request.user.is_authenticated:                                                                                             
                artist_name = getattr(self.request.user, 'stage_name', '') or self.request.user.email.split('@')[0]                                           
                artist, _ = models.Artist.objects.get_or_create(                                                                                              
                    created_by=self.request.user,                                                                                                             
                    defaults={'name': artist_name}                                                                                                            
                )                                                                                                                                             
                                                                                                                                                              
            if artist and artist.created_by is not None and artist.created_by != self.request.user:                                                           
                raise PermissionDenied('Cannot create an album for an artist you do not own.')
  
            album = serializer.save(artist=artist)
            return album
  

class SongViewSet(viewsets.ModelViewSet):
        queryset = models.Song.objects.select_related('artist', 'album').prefetch_related('genres').all()
        serializer_class = serializers.SongSerializer
        permission_classes = [IsAuthenticatedOrReadOnly, permissions.IsOwnerOrReadOnly]
  
        def perform_create(self, serializer):
            artist = serializer.validated_data.get('artist')
            
            if not artist and self.request.user.is_authenticated:
                artist_name = getattr(self.request.user, 'stage_name', '') or self.request.user.email.split('@')[0]
                artist, _ = models.Artist.objects.get_or_create(
                    created_by=self.request.user,
                    defaults={'name': artist_name}
                )
  
            if artist and artist.created_by is not None and artist.created_by != self.request.user:
                raise PermissionDenied('Cannot add songs to an artist you do not own.')
  
            song = serializer.save(artist=artist)
            return song


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
