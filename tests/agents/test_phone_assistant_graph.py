from src.agents.phone_assistant_graph import PhoneAssistantGraph
from src.agents.phone_assistant_nodes import PhoneAssistantNodes
from src.models.graph_state import PhoneAssistantState


class TestAudioService:
    __test__ = False

    def download_recording(self, record_url):
        return "audio/user.mp3"

    def transcribe_mp3(self, mp3_path):
        return "hello"

    def generate_tts(self, text):
        return "ai.wav"


class TestLLMClient:
    __test__ = False

    def generate_structured(self, prompt, dto_type, fallback):
        return fallback

    def generate_text(self, prompt):
        return "hello back"


class TestNewsService:
    __test__ = False

    def get_tamil_nadu_news(self):
        return "news"


class TestTrafficService:
    __test__ = False

    def get_traffic_time(self, start_place, end_place):
        return "traffic"


class TestCallRepository:
    __test__ = False

    def add_call_turn(self, **kwargs):
        self.last_turn = kwargs

    def end_call_session(self, session_id):
        self.ended_session_id = session_id


def test_phone_assistant_graph_runs_general_chat_turn():
    nodes = PhoneAssistantNodes(
        audio_service=TestAudioService(),
        llm_client=TestLLMClient(),
        news_service=TestNewsService(),
        traffic_service=TestTrafficService(),
        call_repository=TestCallRepository(),
    )
    graph = PhoneAssistantGraph(nodes)

    result = graph.run_turn(PhoneAssistantState(session_id="session-1", record_url="https://recording"))

    assert result.user_text == "hello"
    assert result.ai_text == "hello back"
    assert result.ai_audio_file == "ai.wav"
