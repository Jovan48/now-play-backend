import mimetypes

from rest_framework import serializers

from . import models, utils


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
    artist = serializers.PrimaryKeyRelatedField(queryset=models.Artist.objects.all())
    songs = SongNestedSerializer(many=True, read_only=True)

    class Meta:
        model = models.Album
        fields = ['id', 'title', 'artist', 'cover_image', 'release_date', 'created_at', 'songs']
        read_only_fields = ['created_at', 'songs']

    def validate_cover_image(self, cover_image):
        if cover_image is None:
            return cover_image

        valid_types = ['image/jpeg', 'image/png']
        content_type = getattr(cover_image, 'content_type', None) or mimetypes.guess_type(cover_image.name)[0]
        if content_type not in valid_types:
            raise serializers.ValidationError('Cover image must be JPEG or PNG.')
        if cover_image.size > 5 * 1024 * 1024:
            raise serializers.ValidationError('Cover image must be 5MB or smaller.')
        return cover_image


class SongSerializer(serializers.ModelSerializer):
    artist = serializers.PrimaryKeyRelatedField(queryset=models.Artist.objects.all())
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
            'duration',
            'track_number',
            'plays',
            'release_date',
            'genres',
            'created_at',
        ]
        read_only_fields = ['plays', 'created_at']

    def validate_audio_file(self, audio_file):
        valid_types = ['audio/mpeg', 'audio/mp3']
        content_type = getattr(audio_file, 'content_type', None) or mimetypes.guess_type(audio_file.name)[0]
        if content_type not in valid_types:
            raise serializers.ValidationError('Audio file must be MP3.')
        if audio_file.size > 50 * 1024 * 1024:
            raise serializers.ValidationError('Audio file must be 50MB or smaller.')
        return audio_file

    def validate(self, attrs):
        if attrs.get('album') and attrs.get('artist') and attrs['album'].artist != attrs['artist']:
            raise serializers.ValidationError('Album artist must match song artist.')
        return attrs

    def create(self, validated_data):
        genres = validated_data.pop('genres', [])
        song = super().create(validated_data)
        if song.duration in (None, 0):
            song.duration = utils.get_audio_duration(song.audio_file.path)
            song.save(update_fields=['duration'])
        song.genres.set(genres)
        return song

    def update(self, instance, validated_data):
        genres = validated_data.pop('genres', None)
        song = super().update(instance, validated_data)
        if song.duration in (None, 0) and song.audio_file:
            song.duration = utils.get_audio_duration(song.audio_file.path)
            song.save(update_fields=['duration'])
        if genres is not None:
            song.genres.set(genres)
        return song
