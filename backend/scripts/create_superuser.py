import os
import sys
import pathlib
import django

# Ensure the project root (backend/) is on sys.path so `import config` works
BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

    from django.contrib.auth import get_user_model

    User = get_user_model()
    email = os.environ.get('SUPERUSER_EMAIL')
    password = os.environ.get('SUPERUSER_PASSWORD')

    if not email or not password:
        print('SUPERUSER_EMAIL or SUPERUSER_PASSWORD not set; skipping superuser creation.')
        return

    if User.objects.filter(email=email).exists():
        print('Superuser already exists:', email)
        return

    User.objects.create_superuser(email=email, password=password)
    print('Superuser created:', email)


if __name__ == '__main__':
    main()
