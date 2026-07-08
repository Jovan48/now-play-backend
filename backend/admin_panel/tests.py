"""
admin_panel/tests.py

Tests for the admin panel REST API.

These tests cover:
  1. Permission enforcement — unauthenticated, non-staff, and staff access.
  2. AuditLog — starts empty, records actions automatically.
  3. Creator management — list, detail, delete (using the built-in User model,
     so no dependency on the accounts team's models).
  4. Song/Album/Analytics endpoints — graceful 503 when models don't exist.

All tests use djangorestframework-simplejwt to generate tokens directly,
which mirrors how the real frontend authenticates.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from .models import AuditLog

User = get_user_model()


def _jwt(user):
    """Return a valid JWT access token string for the given user."""
    return str(RefreshToken.for_user(user).access_token)


class PermissionTests(TestCase):
    """Verify that IsStaffUser gates every admin endpoint correctly."""

    def setUp(self):
        self.client  = APIClient()
        self.admin   = User.objects.create_superuser(
            username='admin', email='admin@test.com', password='adminpass'
        )
        self.creator = User.objects.create_user(
            username='creator', email='creator@test.com', password='creatorpass'
        )

    # ── Dashboard ─────────────────────────────────────────────────────────

    def test_dashboard_unauthenticated_returns_401(self):
        resp = self.client.get('/api/admin/dashboard/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_dashboard_non_staff_returns_403(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {_jwt(self.creator)}')
        resp = self.client.get('/api/admin/dashboard/')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_dashboard_staff_returns_200(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {_jwt(self.admin)}')
        resp = self.client.get('/api/admin/dashboard/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_dashboard_contains_expected_keys(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {_jwt(self.admin)}')
        resp = self.client.get('/api/admin/dashboard/')
        for key in ('total_creators', 'total_songs', 'total_albums',
                    'pending_songs', 'plays_this_week', 'models_status'):
            self.assertIn(key, resp.data)

    def test_dashboard_models_status_accounts_is_true(self):
        """accounts is always True because we use the built-in User."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {_jwt(self.admin)}')
        resp = self.client.get('/api/admin/dashboard/')
        self.assertTrue(resp.data['models_status']['accounts'])

    # ── Creator list ──────────────────────────────────────────────────────

    def test_creator_list_staff_returns_200(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {_jwt(self.admin)}')
        resp = self.client.get('/api/admin/creators/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_creator_list_excludes_staff_users(self):
        """Staff accounts must not appear in the creator list."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {_jwt(self.admin)}')
        resp = self.client.get('/api/admin/creators/')
        usernames = [u['username'] for u in resp.data['results']]
        self.assertNotIn('admin', usernames)
        self.assertIn('creator', usernames)

    def test_creator_list_search(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {_jwt(self.admin)}')
        resp = self.client.get('/api/admin/creators/?search=creator')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    # ── Creator detail ────────────────────────────────────────────────────

    def test_creator_detail_returns_correct_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {_jwt(self.admin)}')
        resp = self.client.get(f'/api/admin/creators/{self.creator.pk}/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['username'], 'creator')

    def test_creator_detail_404_for_staff(self):
        """Admins cannot look up other staff accounts via the creator endpoint."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {_jwt(self.admin)}')
        resp = self.client.get(f'/api/admin/creators/{self.admin.pk}/')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    # ── Creator delete + AuditLog ─────────────────────────────────────────

    def test_creator_delete_removes_account(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {_jwt(self.admin)}')
        self.client.delete(f'/api/admin/creators/{self.creator.pk}/')
        self.assertFalse(User.objects.filter(pk=self.creator.pk).exists())

    def test_creator_delete_creates_audit_log_entry(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {_jwt(self.admin)}')
        self.client.delete(f'/api/admin/creators/{self.creator.pk}/')
        log = AuditLog.objects.last()
        self.assertIsNotNone(log)
        self.assertEqual(log.action, 'DELETE_CREATOR')
        self.assertEqual(log.target_id, self.creator.pk)

    # ── Audit log endpoint ────────────────────────────────────────────────

    def test_audit_log_starts_empty(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {_jwt(self.admin)}')
        resp = self.client.get('/api/admin/audit-log/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 0)

    def test_audit_log_reflects_action(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {_jwt(self.admin)}')
        self.client.delete(f'/api/admin/creators/{self.creator.pk}/')
        resp = self.client.get('/api/admin/audit-log/')
        self.assertEqual(resp.data['count'], 1)
        self.assertEqual(resp.data['results'][0]['action'], 'DELETE_CREATOR')

    def test_audit_log_non_staff_returns_403(self):
        other = User.objects.create_user(
            username='other', email='other@test.com', password='pass'
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {_jwt(other)}')
        resp = self.client.get('/api/admin/audit-log/')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    # ── 503 fallback for unready models ──────────────────────────────────

    def test_songs_returns_503_before_music_models_defined(self):
        """Song endpoint must not crash — returns 503 when music.Song is absent."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {_jwt(self.admin)}')
        resp = self.client.get('/api/admin/songs/')
        # Either 503 (model not ready) or 200 (model ready) — never 500.
        self.assertIn(
            resp.status_code,
            [status.HTTP_503_SERVICE_UNAVAILABLE, status.HTTP_200_OK],
        )

    def test_albums_returns_503_before_music_models_defined(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {_jwt(self.admin)}')
        resp = self.client.get('/api/admin/albums/')
        self.assertIn(
            resp.status_code,
            [status.HTTP_503_SERVICE_UNAVAILABLE, status.HTTP_200_OK],
        )

    def test_analytics_returns_503_before_analytics_models_defined(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {_jwt(self.admin)}')
        resp = self.client.get('/api/admin/analytics/overview/')
        self.assertIn(
            resp.status_code,
            [status.HTTP_503_SERVICE_UNAVAILABLE, status.HTTP_200_OK],
        )
