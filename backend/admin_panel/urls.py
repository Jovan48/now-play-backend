from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # ── Dashboard ──────────────────────────────────────────────────────────
    path('dashboard/', views.DashboardStatsView.as_view(), name='dashboard'),

    # ── Creator Management ─────────────────────────────────────────────────
    path('creators/',                       views.CreatorListView.as_view(),    name='creator-list'),
    path('creators/<int:pk>/',              views.CreatorDetailView.as_view(),  name='creator-detail'),
    path('creators/<int:pk>/verify/',       views.CreatorVerifyView.as_view(),  name='creator-verify'),
    path('creators/<int:pk>/suspend/',      views.CreatorSuspendView.as_view(), name='creator-suspend'),

    # ── Song Management ────────────────────────────────────────────────────
    path('songs/',                          views.SongListView.as_view(),    name='song-list'),
    path('songs/<int:pk>/',                 views.SongDetailView.as_view(),  name='song-detail'),
    path('songs/<int:pk>/approve/',         views.SongApproveView.as_view(), name='song-approve'),
    path('songs/<int:pk>/reject/',          views.SongRejectView.as_view(),  name='song-reject'),

    # ── Album Management ───────────────────────────────────────────────────
    path('albums/',                         views.AlbumListView.as_view(),   name='album-list'),
    path('albums/<int:pk>/',                views.AlbumDetailView.as_view(), name='album-detail'),

    # ── Analytics ──────────────────────────────────────────────────────────
    path('analytics/overview/',             views.AnalyticsOverviewView.as_view(), name='analytics-overview'),

    # ── Audit Log ──────────────────────────────────────────────────────────
    path('audit-log/',                      views.AuditLogListView.as_view(), name='audit-log'),
]
