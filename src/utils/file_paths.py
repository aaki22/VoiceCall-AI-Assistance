import os
import uuid

from src.constants.audio import GENERATED_AUDIO_DIR, MP3_EXTENSION, WAV_EXTENSION


def ensure_audio_dir() -> None:
    os.makedirs(GENERATED_AUDIO_DIR, exist_ok=True)


def new_audio_path(extension: str = MP3_EXTENSION) -> str:
    ensure_audio_dir()
    return os.path.join(GENERATED_AUDIO_DIR, f"{uuid.uuid4()}{extension}")


def wav_path_for(mp3_path: str) -> str:
    return mp3_path.removesuffix(MP3_EXTENSION) + WAV_EXTENSION


def public_audio_filename(path: str) -> str:
    return os.path.basename(path)
