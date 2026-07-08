from django.urls import path
from .views import (
    LogStreamView,
    LogFollowView,
    ArtistSummaryView,
    ArtistTopSongsView,
    ArtistListeningHistoryView,
    ArtistGeographicView,
    ArtistFollowerGrowthView,
    TopChartsView,
)

urlpatterns = [
    # Event logging
    path('stream/', LogStreamView.as_view(), name='analytics-log-stream'),
    path('follow/', LogFollowView.as_view(), name='analytics-log-follow'),

    # Artist dashboard
    path('artist/summary/', ArtistSummaryView.as_view(), name='analytics-artist-summary'),
    path('artist/top-songs/', ArtistTopSongsView.as_view(), name='analytics-artist-top-songs'),
    path('artist/listening-history/', ArtistListeningHistoryView.as_view(), name='analytics-artist-history'),
    path('artist/geographic/', ArtistGeographicView.as_view(), name='analytics-artist-geographic'),
    path('artist/follower-growth/', ArtistFollowerGrowthView.as_view(), name='analytics-artist-follower-growth'),

    # Public charts
    path('top-charts/', TopChartsView.as_view(), name='analytics-top-charts'),
]
