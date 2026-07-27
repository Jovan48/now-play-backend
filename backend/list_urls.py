import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.urls import get_resolver
for pattern in get_resolver().url_patterns:
    print(pattern)
