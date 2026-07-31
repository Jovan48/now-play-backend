# Generated manually to match `python manage.py makemigrations` output for
# the Song.cover_image field. Run `python manage.py makemigrations --check`
# after applying to confirm Django agrees no further changes are needed.

import music.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0002_alter_artist_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='cover_image',
            field=models.ImageField(blank=True, null=True, upload_to=music.models.song_cover_upload_path),
        ),
    ]
