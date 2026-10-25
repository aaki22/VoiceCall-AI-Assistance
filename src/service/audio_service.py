import logging
import subprocess

from pydub import AudioSegment

from src.client.inworld_tts_client import InworldTTSClient
from src.client.recording_client import RecordingClient
from src.client.speech_recognition_client import SpeechRecognitionClient
from src.constants.audio import DEFAULT_SPEECH_LANGUAGE, WAV_CHANNELS, WAV_FRAME_RATE
from src.exception.exceptions import AudioProcessingException
from src.utils.file_paths import new_audio_path, public_audio_filename, wav_path_for


logger = logging.getLogger(__name__)


class AudioService:
    def __init__(
        self,
        recording_client: RecordingClient,
        tts_client: InworldTTSClient,
        speech_client: SpeechRecognitionClient,
    ):
        self._recording_client = recording_client
        self._tts_client = tts_client
        self._speech_client = speech_client

    def download_recording(self, record_url: str) -> str:
        audio_path = new_audio_path()
        content = self._recording_client.download(record_url)
        with open(audio_path, "wb") as audio_file:
            audio_file.write(content)
        logger.info("Recording saved path=%s", audio_path)
        return audio_path

    def transcribe_mp3(self, mp3_path: str) -> str:
        wav_path = wav_path_for(mp3_path)
        try:
            sound = AudioSegment.from_mp3(mp3_path)
            sound.export(wav_path, format="wav")
        except Exception as exc:
            logger.exception("Recording conversion failed path=%s", mp3_path)
            raise AudioProcessingException("Failed to convert recording for transcription") from exc
        text = self._speech_client.transcribe_wav(wav_path, DEFAULT_SPEECH_LANGUAGE)
        logger.info("Recording transcription completed path=%s empty=%s", mp3_path, not bool(text.strip()))
        return text

    def generate_tts(self, text: str) -> str:
        mp3_path = new_audio_path()
        wav_path = wav_path_for(mp3_path)
        audio_data = self._tts_client.synthesize_mp3(text)

        with open(mp3_path, "wb") as audio_file:
            audio_file.write(audio_data)

        self.convert_to_wav(mp3_path, wav_path)
        logger.info("TTS audio saved mp3=%s wav=%s", mp3_path, wav_path)
        return public_audio_filename(wav_path)

    def convert_to_wav(self, input_mp3: str, output_wav: str) -> None:
        result = subprocess.run(
            ["ffmpeg", "-y", "-i", input_mp3, "-ar", str(WAV_FRAME_RATE), "-ac", str(WAV_CHANNELS), output_wav],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            logger.error("ffmpeg conversion failed input=%s output=%s", input_mp3, output_wav)
            raise AudioProcessingException("Failed to convert TTS output to wav", result.stderr)
