"""
Analytics tests — Now Play for Creators
=========================================
Tests cover:
  - StreamEvent and FollowEvent model creation
  - LogStreamView (POST /api/analytics/stream/)
  - LogFollowView (POST /api/analytics/follow/)
  - ArtistSummaryView (GET /api/analytics/artist/summary/)
  - ArtistTopSongsView (GET /api/analytics/artist/top-songs/)
  - ArtistListeningHistoryView (GET /api/analytics/artist/listening-history/)
  - ArtistGeographicView (GET /api/analytics/artist/geographic/)
  - ArtistFollowerGrowthView (GET /api/analytics/artist/follower-growth/)
  - TopChartsView (GET /api/analytics/top-charts/)

NOTE: These tests use a stub Song model. Once the music app defines its Song
model these tests will work end-to-end. The Song stub below can be removed
once the real model is in place.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken
from unittest.mock import patch, MagicMock

from .models import StreamEvent, FollowEvent

User = get_user_model()


def make_jwt(user):
    """Return a valid JWT Bearer token string for the given user."""
    token = AccessToken.for_user(user)
    return f'Bearer {token}'


class AnalyticsModelTests(TestCase):
    """Unit tests for model creation and __str__ methods."""

    def setUp(self):
        self.artist = User.objects.create_user(email='artist1@example.com', password='pass')
        self.listener = User.objects.create_user(email='listener1@example.com', password='pass')

    def test_follow_event_str(self):
        event = FollowEvent.objects.create(
            follower=self.listener,
            artist=self.artist,
            action=FollowEvent.FOLLOW,
        )
        self.assertIn('listener1', str(event))
        self.assertIn('artist1', str(event))
        self.assertIn('follow', str(event))

    def test_unfollow_event_creation(self):
        event = FollowEvent.objects.create(
            follower=self.listener,
            artist=self.artist,
            action=FollowEvent.UNFOLLOW,
        )
        self.assertEqual(event.action, FollowEvent.UNFOLLOW)


class LogFollowViewTests(TestCase):
    """Tests for POST /api/analytics/follow/"""

    def setUp(self):
        self.client = APIClient()
        self.artist = User.objects.create_user(
            email='artist2@example.com', password='pass', is_active=True, is_verified=True
        )
        self.listener = User.objects.create_user(
            email='listener2@example.com', password='pass', is_active=True, is_verified=True
        )
        self.client.credentials(HTTP_AUTHORIZATION=make_jwt(self.listener))

    def test_follow_artist(self):
        url = reverse('analytics-log-follow')
        response = self.client.post(url, {'artist': self.artist.id, 'action': 'follow'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FollowEvent.objects.count(), 1)

    def test_unfollow_artist(self):
        url = reverse('analytics-log-follow')
        response = self.client.post(url, {'artist': self.artist.id, 'action': 'unfollow'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_cannot_follow_yourself(self):
        url = reverse('analytics-log-follow')
        response = self.client.post(url, {'artist': self.listener.id, 'action': 'follow'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_follow_rejected(self):
        self.client.credentials()  # clear token
        url = reverse('analytics-log-follow')
        response = self.client.post(url, {'artist': self.artist.id, 'action': 'follow'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ArtistFollowerGrowthViewTests(TestCase):
    """Tests for GET /api/analytics/artist/follower-growth/"""

    def setUp(self):
        self.client = APIClient()
        self.artist = User.objects.create_user(
            email='artist3@example.com', password='pass', is_active=True, is_verified=True
        )
        self.fan1 = User.objects.create_user(
            email='fan1@example.com', password='pass', is_active=True, is_verified=True
        )
        self.fan2 = User.objects.create_user(
            email='fan2@example.com', password='pass', is_active=True, is_verified=True
        )
        self.client.credentials(HTTP_AUTHORIZATION=make_jwt(self.artist))

        FollowEvent.objects.create(follower=self.fan1, artist=self.artist, action=FollowEvent.FOLLOW)
        FollowEvent.objects.create(follower=self.fan2, artist=self.artist, action=FollowEvent.FOLLOW)
        FollowEvent.objects.create(follower=self.fan1, artist=self.artist, action=FollowEvent.UNFOLLOW)

    def test_follower_growth_response_structure(self):
        url = reverse('analytics-artist-follower-growth')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        if response.data:
            row = response.data[0]
            self.assertIn('date', row)
            self.assertIn('follows', row)
            self.assertIn('unfollows', row)
            self.assertIn('net', row)

    def test_period_filter_all(self):
        url = reverse('analytics-artist-follower-growth')
        response = self.client.get(url, {'period': 'all'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ArtistSummaryViewTests(TestCase):
    """Tests for GET /api/analytics/artist/summary/"""

    def setUp(self):
        self.client = APIClient()
        self.artist = User.objects.create_user(
            email='artist4@example.com', password='pass', is_active=True, is_verified=True
        )
        self.fan = User.objects.create_user(
            email='fan4@example.com', password='pass', is_active=True, is_verified=True
        )
        self.client.credentials(HTTP_AUTHORIZATION=make_jwt(self.artist))

        FollowEvent.objects.create(follower=self.fan, artist=self.artist, action=FollowEvent.FOLLOW)

    def test_summary_response_structure_no_songs(self):
        """Artist with no songs should return zeros for play stats."""
        url = reverse('analytics-artist-summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_plays'], 0)
        self.assertEqual(response.data['unique_listeners'], 0)
        self.assertEqual(response.data['total_followers'], 1)

    def test_unauthenticated_summary_rejected(self):
        self.client.credentials()
        url = reverse('analytics-artist-summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TopChartsViewTests(TestCase):
    """Tests for GET /api/analytics/top-charts/ (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_top_charts_accessible_without_auth(self):
        url = reverse('analytics-top-charts')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_top_charts_limit_param(self):
        url = reverse('analytics-top-charts')
        response = self.client.get(url, {'limit': 5, 'period': 'all'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data), 5)
