from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AccountsAuthTests(APITestCase):
    def test_registration_requires_email_and_password(self):
        url = reverse('accounts:register')
        payload = {
            'email': 'creator@example.com',
            'full_name': 'Test Creator',
            'stage_name': 'Creator Test',
            'password': 'pass1234',
            'password2': 'pass1234',
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=payload['email'])
        self.assertFalse(user.is_verified)
        self.assertFalse(user.is_active)

    def test_login_fails_before_email_verification(self):
        user = User.objects.create_user(email='test@example.com', password='pass1234', full_name='Test')
        url = reverse('accounts:token_obtain_pair')
        response = self.client.post(url, {'email': user.email, 'password': 'pass1234'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_verify_email_then_login(self):
        user = User.objects.create_user(email='verify@example.com', password='pass1234', full_name='Verify Test')
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        verify_url = reverse('accounts:verify-email') + f'?uid={uid}&token={token}'
        response = self.client.get(verify_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_verified)
        self.assertTrue(user.is_active)
        login_url = reverse('accounts:token_obtain_pair')
        login_response = self.client.post(login_url, {'email': user.email, 'password': 'pass1234'}, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', login_response.data)

    def test_profile_update(self):
        user = User.objects.create_user(email='profile@example.com', password='pass1234', full_name='Profile Test', is_active=True, is_verified=True)
        profile_url = reverse('accounts:profile')
        self.client.force_authenticate(user=user)
        response = self.client.put(profile_url, {
            'full_name': 'Profile Updated',
            'stage_name': 'Updated',
            'bio': 'Creator bio',
            'genres': ['hip hop'],
            'city': 'Kampala',
            'country': 'Uganda',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.full_name, 'Profile Updated')
        self.assertEqual(user.stage_name, 'Updated')
        self.assertEqual(user.city, 'Kampala')
        self.assertEqual(user.country, 'Uganda')
