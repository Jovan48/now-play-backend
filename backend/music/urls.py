from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'songs', views.SongViewSet, basename='song')
router.register(r'tracks', views.SongViewSet, basename='track')
router.register(r'albums', views.AlbumViewSet, basename='album')
router.register(r'artists', views.ArtistViewSet, basename='artist')
router.register(r'genres', views.GenreViewSet, basename='genre')

urlpatterns = [
    path('', include(router.urls)),
    path('search/', views.SearchView.as_view(), name='music-search'),
]