import logging
import os
import requests

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import signing  # <-- NEW: For secure magic link tokens
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import (
    EmailVerificationSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
    RegistrationSerializer,
    UserProfileSerializer,
    MagicLinkRequestSerializer,
    MagicLinkVerifySerializer,
    LogoutSerializer,
)

logger = logging.getLogger(__name__)
User = get_user_model()


def _send_message(subject, body, recipient_list):
    api_key = os.environ.get('BREVO_API_KEY')
    sender_email = os.environ.get('BREVO_SENDER_EMAIL')

    if not api_key or not sender_email:
        logger.error('Brevo not configured: missing BREVO_API_KEY or BREVO_SENDER_EMAIL')
        return

    for recipient in recipient_list:
        try:
            resp = requests.post(
                'https://api.brevo.com/v3/smtp/email',
                headers={
                    'accept': 'application/json',
                    'api-key': api_key,
                    'content-type': 'application/json',
                },
                json={
                    'sender': {'email': sender_email, 'name': 'Now Play'},
                    'to': [{'email': recipient}],
                    'subject': subject,
                    'textContent': body,
                },
                timeout=10,
            )
            resp.raise_for_status()
        except requests.HTTPError as exc:
            logger.error(
                'Failed to send email to %s via Brevo: %s — %s',
                recipient, exc, resp.text if 'resp' in locals() else ''
            )
        except requests.RequestException as exc:
            logger.error('Failed to send email to %s via Brevo: %s', recipient, exc)


def build_frontend_url(path_segment, uid, token):
    """Build a URL pointing at the Vercel frontend so the user lands on the UI, not the raw API."""
    base = settings.FRONTEND_URL.rstrip('/')
    return f'{base}/{path_segment}?uid={uid}&token={token}'


def send_verification_email(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    url = build_frontend_url('verify-email', uid, token)
    body = (
        f'Welcome to Now Play!\n\n'
        f'Please verify your email address by visiting the link below:\n\n{url}\n\n'
        'If you did not request this, please ignore this message.'
    )
    _send_message('Verify your Now Play account', body, [user.email])


def send_password_reset_email(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    url = build_frontend_url('reset-password', uid, token)
    body = (
        f'You requested a password reset for your Now Play account.\n\n'
        f'Use the link below to set a new password:\n\n{url}\n\n'
        'If you did not request this, please ignore this message.'
    )
    _send_message('Reset your Now Play password', body, [user.email])


# ==========================================
# NEW: MAGIC LINK HELPER
# ==========================================
def send_magic_link_email(email):
    """Generates a time-limited token and sends the magic link."""
    signer = signing.TimestampSigner()
    token = signer.sign(email)
    
    base = settings.FRONTEND_URL.rstrip('/')
    url = f'{base}/verify-magic-link?token={token}'
    
    body = (
        f'Here is your magic link to sign in to Now Play!\n\n'
        f'Click the link below to log in or create your account:\n\n{url}\n\n'
        'This link will expire in 15 minutes. If you did not request this, please ignore this message.'
    )
    _send_message('Your Now Play Magic Link', body, [email])


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user.is_active or not self.user.is_verified:
            raise AuthenticationFailed('Unable to log in with provided credentials.', code='authentication')
        return data


class RegisterView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = User.objects.get(email=response.data['email'])
        try:
            send_verification_email(user)
        except Exception as exc:
            logger.error('Failed to send verification email to %s: %s', user.email, exc)
        return Response(
            {'detail': 'Registration successful. Check your email to verify your account.'},
            status=status.HTTP_201_CREATED,
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer  # <-- ADDED THIS
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        refresh_token = serializer.validated_data['refresh']
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response({'detail': 'Invalid refresh token.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_205_RESET_CONTENT)


class EmailVerificationView(generics.GenericAPIView):
    serializer_class = EmailVerificationSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        uid = serializer.validated_data['uid']
        token = serializer.validated_data['token']
        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = get_object_or_404(User, pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'detail': 'Invalid verification link.'}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            user.is_verified = True
            user.is_active = True
            user.save(update_fields=['is_verified', 'is_active'])
            return Response({'detail': 'Email verified. You may now log in.'}, status=status.HTTP_200_OK)

        return Response({'detail': 'Invalid or expired verification token.'}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.filter(email__iexact=email).first()
        if user:
            send_password_reset_email(user)
        return Response({'detail': 'If the email exists, a password reset link has been sent.'}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uid = serializer.validated_data['uid']
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = get_object_or_404(User, pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'detail': 'Invalid reset link.'}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({'detail': 'Invalid or expired reset token.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({'detail': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# ==========================================
# NEW: MAGIC LINK VIEWS
# ==========================================

class SendMagicLinkView(generics.GenericAPIView):
    """
    Accepts an email, generates a secure time-limited token, 
    and sends a magic link pointing to the frontend.
    """
    serializer_class = MagicLinkRequestSerializer  # <-- ADDED THIS
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # Use the serializer to validate the email
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email'].strip().lower()
        
        try:
            send_magic_link_email(email)
        except Exception as exc:
            logger.error('Failed to send magic link email to %s: %s', email, exc)
            
        # Always return 200 to prevent email enumeration attacks
        return Response({'detail': 'If the email is valid, a magic link has been sent.'}, status=status.HTTP_200_OK)


class VerifyMagicLinkView(generics.GenericAPIView):
    """
    Accepts the magic link token, verifies it, creates/gets the user,
    and returns JWT tokens.
    """
    serializer_class = MagicLinkVerifySerializer  # <-- ADDED THIS
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # Use the serializer to validate the token
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']

        signer = signing.TimestampSigner()
        try:
            # Verify token signature and ensure it's not older than 15 minutes (900 seconds)
            email = signer.unsign(token, max_age=900)
        except signing.SignatureExpired:
            return Response({'detail': 'Magic link has expired. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)
        except signing.BadSignature:
            return Response({'detail': 'Invalid or tampered magic link.'}, status=status.HTTP_400_BAD_REQUEST)

        email = email.strip().lower()

        # Get or create the user (Passwordless sign-up/login)
        user, created = User.objects.get_or_create(
            email=email,
            defaults={'is_verified': True, 'is_active': True}
        )
        
        # If user existed but wasn't verified, verify them now since they proved email ownership
        if not created and not user.is_verified:
            user.is_verified = True
            user.is_active = True
            user.save(update_fields=['is_verified', 'is_active'])
            
        if not user.is_active:
            return Response({'detail': 'This account has been deactivated.'}, status=status.HTTP_403_FORBIDDEN)

        # Generate JWT tokens for the frontend
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'is_new_user': created,
            'detail': 'Successfully authenticated.'
        }, status=status.HTTP_200_OK)