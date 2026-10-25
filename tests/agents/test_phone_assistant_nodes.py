from src.agents.phone_assistant_nodes import PhoneAssistantNodes, route_intent
from src.models.graph_state import PhoneAssistantState
from src.models.intent import AssistantIntent, TrafficIntent


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

    def __init__(self):
        self.ended = False
        self.turns = []

    def add_call_turn(self, **kwargs):
        self.turns.append(kwargs)

    def end_call_session(self, session_id):
        self.ended = True


def make_nodes(repo=None):
    return PhoneAssistantNodes(
        audio_service=TestAudioService(),
        llm_client=TestLLMClient(),
        news_service=TestNewsService(),
        traffic_service=TestTrafficService(),
        call_repository=repo or TestCallRepository(),
    )


def test_route_intent_routes_current_features():
    assert route_intent(PhoneAssistantState(session_id="1", intent=TrafficIntent.TRAFFIC.value)) == "traffic"
    assert route_intent(PhoneAssistantState(session_id="1", intent=AssistantIntent.TAMIL_NADU_NEWS.value)) == "news"
    assert route_intent(PhoneAssistantState(session_id="1", intent="general_chat")) == "general_chat"


def test_nodes_persist_and_end_call():
    repo = TestCallRepository()
    nodes = make_nodes(repo)
    state = PhoneAssistantState(session_id="1", user_text="bye", ai_text="bye", user_audio_path="u.mp3", ai_audio_file="a.wav")

    nodes.persist_turn(state)
    nodes.check_end_call(state)

    assert repo.turns
    assert repo.ended is True
    assert state.should_end_call is True
