from src.models.graph_state import PhoneAssistantState
from src.service.audio_service import AudioService
from src.service.conversation_service import ConversationService, build_record_xml


class TestRecordingClient:
    __test__ = False

    def download(self, record_url):
        return b"audio"


class TestTTSClient:
    __test__ = False

    def synthesize_mp3(self, text):
        return b"mp3"


class TestSpeechClient:
    __test__ = False

    def transcribe_wav(self, wav_path, language):
        return "transcribed"


class TestRepo:
    __test__ = False

    def create_call_session(self, session_id):
        self.session_id = session_id


class TestGraph:
    __test__ = False

    def run_turn(self, state):
        state.ai_text = "ok"
        return state


def test_audio_service_downloads_recording(monkeypatch, tmp_path):
    target = tmp_path / "audio.mp3"
    monkeypatch.setattr("src.service.audio_service.new_audio_path", lambda: str(target))

    path = AudioService(TestRecordingClient(), TestTTSClient(), TestSpeechClient()).download_recording("url")

    assert path == str(target)
    assert target.read_bytes() == b"audio"


def test_audio_service_generate_tts_writes_and_returns_filename(monkeypatch, tmp_path):
    target = tmp_path / "voice.mp3"
    monkeypatch.setattr("src.service.audio_service.new_audio_path", lambda: str(target))
    monkeypatch.setattr(AudioService, "convert_to_wav", lambda self, source, dest: None)

    filename = AudioService(TestRecordingClient(), TestTTSClient(), TestSpeechClient()).generate_tts("hello")

    assert filename == "voice.wav"
    assert target.read_bytes() == b"mp3"


def test_conversation_service_start_and_process(monkeypatch):
    monkeypatch.setattr("src.service.conversation_service.uuid.uuid4", lambda: "uuid")
    service = ConversationService(TestRepo(), AudioService(TestRecordingClient(), TestTTSClient(), TestSpeechClient()), TestGraph())
    monkeypatch.setattr(service._audio_service, "generate_tts", lambda text: "greeting.wav")

    session_id, audio_file = service.start_call()
    state = service.process_recording(session_id, "url")

    assert session_id == "uuid"
    assert audio_file == "greeting.wav"
    assert isinstance(state, PhoneAssistantState)
    assert build_record_xml(session_id).startswith("<Record")
