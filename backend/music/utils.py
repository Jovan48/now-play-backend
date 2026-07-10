import os

from mutagen import File
from mutagen.id3 import ID3NoHeaderError
from mutagen.mp3 import HeaderNotFoundError


def extract_id3_tags(file_path):
    try:
        audio = File(file_path, easy=True)
    except (ID3NoHeaderError, HeaderNotFoundError):
        return {}

    if audio is None:
        return {}

    return {
        'title': audio.get('title', [None])[0],
        'artist': audio.get('artist', [None])[0],
        'album': audio.get('album', [None])[0],
        'track_number': audio.get('tracknumber', [None])[0],
        'year': audio.get('date', [None])[0],
    }


def get_audio_duration(file_path):
    if not os.path.exists(file_path):
        return None

    try:
        audio = File(file_path)
    except (ID3NoHeaderError, HeaderNotFoundError):
        return None

    if audio is None or not hasattr(audio.info, 'length'):
        return None

    return int(round(audio.info.length))
