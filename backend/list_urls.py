import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from music import urls as music_urls

for route in music_urls.router.urls:
    print(route.pattern)
