from src.constants.audio import MP3_EXTENSION
from src.utils.file_paths import public_audio_filename, wav_path_for


def test_wav_path_for_replaces_mp3_extension():
    assert wav_path_for("audio/test.mp3") == "audio/test.wav"


def test_public_audio_filename_returns_basename():
    assert public_audio_filename("audio/test.wav") == "test.wav"


def test_mp3_extension_constant_is_stable():
    assert MP3_EXTENSION == ".mp3"
