import mimetypes

from django.http import QueryDict
from rest_framework import serializers

from . import models, utils


def _mutable_copy(data):
    # QueryDict is a dict subclass, so isinstance(data, dict) is True for
    # multipart/form-data. QueryDict.copy() is a DEEP copy under the hood
    # (self.__deepcopy__({})) and crashes on uploaded files:
    # "TypeError: cannot pickle 'BufferedRandom' instances". Rebuild via
    # setlist instead, which copies references, not file contents.
    if isinstance(data, QueryDict):
        new_data = QueryDict(mutable=True)
        for key in data:
            new_data.setlist(key, data.getlist(key))
        return new_data
    if isinstance(data, dict):
        return data.copy()
    if hasattr(data, 'dict'):
        return data.dict()
    if hasattr(data, 'items'):
        return dict(data.items())
    return data


def _validate_cover_image(cover_image):
    if cover_image is None:
        return cover_image

    valid_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    content_type = getattr(cover_image, 'content_type', None) or mimetypes.guess_type(cover_image.name)[0]
    if content_type not in valid_types and not cover_image.name.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
        raise serializers.ValidationError('Cover image must be JPEG, PNG, or WebP.')
    if cover_image.size > 10 * 1024 * 1024:
        raise serializers.ValidationError('Cover image must be 10MB or smaller.')
    return cover_image


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Genre
        fields = ['id', 'name', 'slug']


class SongNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Song
        fields = ['id', 'title', 'track_number', 'plays']


class AlbumNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Album
        fields = ['id', 'title', 'release_date']


class ArtistSerializer(serializers.ModelSerializer):
    albums = AlbumNestedSerializer(many=True, read_only=True)
    songs = SongNestedSerializer(many=True, read_only=True)

    class Meta:
        model = models.Artist
        fields = ['id', 'name', 'bio', 'photo', 'created_by', 'created_at', 'albums', 'songs']
        read_only_fields = ['created_by', 'created_at', 'albums', 'songs']


class AlbumSerializer(serializers.ModelSerializer):
    artist = serializers.PrimaryKeyRelatedField(queryset=models.Artist.objects.all(), required=False)
    songs = SongNestedSerializer(many=True, read_only=True)

    class Meta:
        model = models.Album
        fields = ['id', 'title', 'artist', 'cover_image', 'release_date', 'created_at', 'songs']
        read_only_fields = ['created_at', 'songs']

    def to_internal_value(self, data):
        data = _mutable_copy(data)

        if isinstance(data, dict):
            if 'coverImage' in data and 'cover_image' not in data:
                data['cover_image'] = data.pop('coverImage')
            if 'releaseDate' in data and 'release_date' not in data:
                data['release_date'] = data.pop('releaseDate')
            if 'artistId' in data and 'artist' not in data:
                data['artist'] = data.pop('artistId')
            if 'artist_id' in data and 'artist' not in data:
                data['artist'] = data.pop('artist_id')

            # Handle string artist names
            artist_val = data.get('artist') or data.get('artist_name') or data.get('artistName')
            if isinstance(artist_val, str) and not artist_val.isdigit():
                user = self.context.get('request').user if self.context.get('request') else None
                artist_obj, _ = models.Artist.objects.get_or_create(
                    name=artist_val,
                    defaults={'created_by': user if (user and user.is_authenticated) else None}
                )
                data['artist'] = artist_obj.pk
        return super().to_internal_value(data)

    def validate_cover_image(self, cover_image):
        return _validate_cover_image(cover_image)


class SongSerializer(serializers.ModelSerializer):
    artist = serializers.PrimaryKeyRelatedField(queryset=models.Artist.objects.all(), required=False)
    album = serializers.PrimaryKeyRelatedField(queryset=models.Album.objects.all(), allow_null=True, required=False)
    genres = serializers.PrimaryKeyRelatedField(queryset=models.Genre.objects.all(), many=True, required=False)

    class Meta:
        model = models.Song
        fields = [
            'id',
            'title',
            'artist',
            'album',
            'audio_file',
            'cover_image',
            'duration',
            'track_number',
            'plays',
            'release_date',
            'genres',
            'created_at',
        ]
        read_only_fields = ['plays', 'created_at']

    def to_internal_value(self, data):
        data = _mutable_copy(data)

        if isinstance(data, dict):
            if 'audioFile' in data and 'audio_file' not in data:
                data['audio_file'] = data.pop('audioFile')
            if 'coverImage' in data and 'cover_image' not in data:
                data['cover_image'] = data.pop('coverImage')
            if 'trackNumber' in data and 'track_number' not in data:
                data['track_number'] = data.pop('trackNumber')
            if 'releaseDate' in data and 'release_date' not in data:
                data['release_date'] = data.pop('releaseDate')
            if 'artistId' in data and 'artist' not in data:
                data['artist'] = data.pop('artistId')
            if 'artist_id' in data and 'artist' not in data:
                data['artist'] = data.pop('artist_id')
            if 'albumId' in data and 'album' not in data:
                data['album'] = data.pop('albumId')
            if 'album_id' in data and 'album' not in data:
                data['album'] = data.pop('album_id')

            # Handle string artist names seamlessly
            artist_val = data.get('artist') or data.get('artist_name') or data.get('artistName')
            if isinstance(artist_val, str) and not artist_val.isdigit():
                user = self.context.get('request').user if self.context.get('request') else None
                artist_obj, _ = models.Artist.objects.get_or_create(
                    name=artist_val,
                    defaults={'created_by': user if (user and user.is_authenticated) else None}
                )
                data['artist'] = artist_obj.pk

        return super().to_internal_value(data)

    def validate_audio_file(self, audio_file):
        if not audio_file:
            return audio_file
        valid_types = [
            'audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/x-wav', 'audio/wave',
            'audio/flac', 'audio/x-flac', 'audio/aac', 'audio/mp4', 'audio/m4a',
            'audio/x-m4a', 'audio/ogg', 'audio/webm', 'application/octet-stream'
        ]
        content_type = getattr(audio_file, 'content_type', None) or mimetypes.guess_type(audio_file.name)[0]
        ext = audio_file.name.lower().split('.')[-1] if '.' in audio_file.name else ''
        valid_exts = ['mp3', 'wav', 'flac', 'aac', 'm4a', 'mp4', 'ogg', 'webm']
        
        if content_type not in valid_types and ext not in valid_exts:
            raise serializers.ValidationError('Audio file must be MP3, WAV, FLAC, M4A, or AAC.')
        if audio_file.size > 100 * 1024 * 1024:
            raise serializers.ValidationError('Audio file must be 100MB or smaller.')
        return audio_file

    def validate_cover_image(self, cover_image):
        return _validate_cover_image(cover_image)

    def validate(self, attrs):
        # Auto-set artist from album if album is provided but artist is omitted
        if attrs.get('album') and not attrs.get('artist'):
            attrs['artist'] = attrs['album'].artist

        if attrs.get('album') and attrs.get('artist') and attrs['album'].artist != attrs['artist']:
            raise serializers.ValidationError({'album': 'Album artist must match song artist.'})
        return attrs

    def create(self, validated_data):
        genres = validated_data.pop('genres', [])
        song = super().create(validated_data)
        if song.duration in (None, 0) and song.audio_file:
            try:
                song.duration = utils.get_audio_duration(song.audio_file.path)
                song.save(update_fields=['duration'])
            except Exception:
                pass
        if genres:
            song.genres.set(genres)
        return song

    def update(self, instance, validated_data):
        genres = validated_data.pop('genres', None)
        song = super().update(instance, validated_data)
        if song.duration in (None, 0) and song.audio_file:
            try:
                song.duration = utils.get_audio_duration(song.audio_file.path)
                song.save(update_fields=['duration'])
            except Exception:
                pass
        if genres is not None:
            song.genres.set(genres)
        return song