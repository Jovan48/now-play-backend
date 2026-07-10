import os
import re

from django.core.files import File as DjangoFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from music.models import Album, Artist, Genre, Song
from music.utils import extract_id3_tags, get_audio_duration


TRACK_NUMBER_PATTERN = re.compile(r'^(\d+)')


def parse_track_number(track_number):
    if not track_number:
        return None
    if isinstance(track_number, (list, tuple)):
        track_number = track_number[0]
    if isinstance(track_number, int):
        return track_number
    match = TRACK_NUMBER_PATTERN.match(str(track_number).strip())
    return int(match.group(1)) if match else None


class Command(BaseCommand):
    help = 'Import local MP3 files from a folder into the music catalog.'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str, help='Path to a folder containing MP3 files.')
        parser.add_argument(
            '--genre',
            action='append',
            dest='genres',
            default=[],
            help='Add one or more genres to imported songs.',
        )

    def handle(self, *args, **options):
        root_path = options['path']
        assigned_genres = options['genres']

        if not os.path.isdir(root_path):
            raise CommandError(f'Path does not exist or is not a directory: {root_path}')

        self.stdout.write(self.style.NOTICE(f'Scanning {root_path} for MP3 files...'))
        imported = 0
        skipped = 0
        failed = 0

        for dirpath, _, filenames in os.walk(root_path):
            for filename in sorted(filenames):
                if not filename.lower().endswith('.mp3'):
                    continue

                file_path = os.path.join(dirpath, filename)
                self.stdout.write(f'Processing: {file_path}')

                try:
                    metadata = extract_id3_tags(file_path)
                    title = metadata.get('title') or os.path.splitext(filename)[0]
                    artist_name = metadata.get('artist') or os.path.basename(os.path.dirname(file_path)) or 'Unknown Artist'
                    album_title = metadata.get('album') or 'Unknown Album'
                    track_number = parse_track_number(metadata.get('track_number'))
                    year = metadata.get('year')

                    with transaction.atomic():
                        artist, _ = Artist.objects.get_or_create(name=artist_name)
                        album, _ = Album.objects.get_or_create(title=album_title, artist=artist)

                        duplicate_filter = {
                            'title': title,
                            'artist': artist,
                            'album': album,
                        }
                        if Song.objects.filter(**duplicate_filter).exists():
                            skipped += 1
                            self.stdout.write(self.style.WARNING(f'Skipped duplicate: {title} by {artist.name}'))
                            continue

                        with open(file_path, 'rb') as fp:
                            django_file = DjangoFile(fp, name=filename)
                            song = Song.objects.create(
                                title=title,
                                artist=artist,
                                album=album,
                                audio_file=django_file,
                                duration=get_audio_duration(file_path),
                                track_number=track_number,
                                release_date=year or None,
                            )

                        if assigned_genres:
                            genre_objects = []
                            for genre_label in assigned_genres:
                                genre_obj, _ = Genre.objects.get_or_create(name=genre_label.strip(), slug=genre_label.strip().lower().replace(' ', '-'))
                                genre_objects.append(genre_obj)
                            song.genres.set(genre_objects)

                        imported += 1
                        self.stdout.write(self.style.SUCCESS(f'Imported: {title}'))
                except Exception as exc:
                    failed += 1
                    self.stdout.write(self.style.ERROR(f'Failed to import {file_path}: {exc}'))

        self.stdout.write(self.style.SUCCESS(f'Done. Imported: {imported}, Skipped: {skipped}, Failed: {failed}'))
