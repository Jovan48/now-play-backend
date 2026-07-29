from django.urls import path

from .views import (
    CustomTokenObtainPairView,
    EmailVerificationView,
    LogoutView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegisterView,
    SendMagicLinkView,     # <-- NEW
    TokenRefreshView,
    UserProfileView,
    VerifyMagicLinkView,   # <-- NEW
)

app_name = 'accounts'

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/verify-email/', EmailVerificationView.as_view(), name='verify-email'),
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('auth/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    
    # ==========================================
    # NEW: MAGIC LINK ENDPOINTS
    # ==========================================
    path('auth/magic-link/', SendMagicLinkView.as_view(), name='send-magic-link'),
    path('auth/verify-magic-link/', VerifyMagicLinkView.as_view(), name='verify-magic-link'),
    
    path('profile/', UserProfileView.as_view(), name='profile'),
]