import os
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Album, Artist, Genre, Song
from .utils import extract_id3_tags, get_audio_duration


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(prefix='music_test_media_'))
class MusicAppTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = self._create_user('creator@example.com', 'password123')
        self.other_user = self._create_user('other@example.com', 'password123')
        self.artist = Artist.objects.create(name='Test Artist')
        self.album = Album.objects.create(title='Test Album', artist=self.artist)

    def _create_user(self, email, password):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        return User.objects.create_user(email=email, password=password)

    def _make_mp3_file(self, name='song.mp3', content=b'Fake mp3 content'):
        return SimpleUploadedFile(name, content, content_type='audio/mpeg')

    def test_delete_album_keeps_song(self):
        song = Song.objects.create(
            title='Song One',
            artist=self.artist,
            album=self.album,
            audio_file=self._make_mp3_file(),
            duration=120,
        )
        self.album.delete()
        song.refresh_from_db()
        self.assertIsNone(song.album)

    def test_extract_id3_tags_handles_invalid_file(self):
        invalid_path = os.path.join(settings.MEDIA_ROOT, 'invalid.mp3')
        with open(invalid_path, 'wb') as fp:
            fp.write(b'Not a valid mp3 file')

        tags = extract_id3_tags(invalid_path)
        self.assertIsInstance(tags, dict)
        self.assertEqual(tags, {})

    def test_get_audio_duration_returns_none_for_invalid_file(self):
        invalid_path = os.path.join(settings.MEDIA_ROOT, 'invalid.mp3')
        with open(invalid_path, 'wb') as fp:
            fp.write(b'Not a valid mp3 file')

        duration = get_audio_duration(invalid_path)
        self.assertIsNone(duration)

    def test_unauthenticated_user_cannot_create_song(self):
        url = reverse('song-list')
        response = self.client.post(url, {'title': 'Unauth', 'artist': self.artist.id})
        self.assertEqual(response.status_code, 401)

    def test_authenticated_user_can_create_song_and_play(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('song-list')
        song_file = self._make_mp3_file()
        response = self.client.post(url, {
            'title': 'First Song',
            'artist': self.artist.id,
            'album': self.album.id,
            'audio_file': song_file,
            'track_number': 1,
        }, format='multipart')

        self.assertEqual(response.status_code, 201)
        song_id = response.data['id']
        play_url = reverse('song-play', kwargs={'pk': song_id})
        play_response = self.client.post(play_url)
        self.assertEqual(play_response.status_code, 200)
        self.assertEqual(play_response.data['plays'], 1)

    def test_non_owner_cannot_edit_song(self):
        self.artist.created_by = self.other_user
        self.artist.save(update_fields=['created_by'])
        song = Song.objects.create(
            title='Owned Song',
            artist=self.artist,
            album=self.album,
            audio_file=self._make_mp3_file(),
            duration=90,
        )

        self.client.force_authenticate(user=self.user)
        url = reverse('song-detail', kwargs={'pk': song.id})
        response = self.client.patch(url, {'title': 'Hacked Title'}, format='json')
        self.assertEqual(response.status_code, 403)

    def test_audio_file_validation_rejects_invalid_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('song-list')
        invalid_file = SimpleUploadedFile('song.wav', b'Fake content', content_type='audio/wav')
        response = self.client.post(url, {
            'title': 'Invalid File',
            'artist': self.artist.id,
            'audio_file': invalid_file,
        }, format='multipart')
        self.assertEqual(response.status_code, 400)
        self.assertIn('audio_file', response.data)

    def test_search_endpoint_returns_matching_items(self):
        song = Song.objects.create(
            title='Searchable Song',
            artist=self.artist,
            album=self.album,
            audio_file=self._make_mp3_file(),
            duration=100,
        )
        self.artist.name = 'Search Artist'
        self.artist.save(update_fields=['name'])
        self.album.title = 'Search Album'
        self.album.save(update_fields=['title'])

        url = reverse('music-search')
        response = self.client.get(url, {'q': 'Search'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['songs']), 1)
        self.assertEqual(len(response.data['albums']), 1)
        self.assertEqual(len(response.data['artists']), 1)
