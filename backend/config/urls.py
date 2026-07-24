from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny

urlpatterns = [                                                          
        path('admin/', admin.site.urls),                                     
        path('api/schema/', SpectacularAPIView.                              
  as_view(permission_classes=[AllowAny]), name='schema'),                    
        path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema', permission_classes=[AllowAny]), name='swagger-ui'),
        
        # Mounting accounts under 'api/' directly:
        path('api/', include('accounts.urls')),
        
        path('api/music/', include('music.urls')),
        path('api/tracks/', include('music.urls')),
        path('api/playlists/', include('playlists.urls')),
        path('api/albums/', include('music.urls')),
        path('api/analytics/', include('analytics.urls')),
        path('api/admin/', include('admin_panel.urls')),
    ]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
