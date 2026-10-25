import logging

from langdetect import detect

from src.client.llm_client import LLMClient
from src.models.graph_state import PhoneAssistantState
from src.models.intent import AssistantIntent, AssistantIntentOutput, TrafficIntent, TrafficIntentOutput
from src.prompts.assistant_prompts import GENERAL_ASSISTANT_PROMPT
from src.prompts.intent_prompts import ASSISTANT_INTENT_PROMPT, TRAFFIC_INTENT_PROMPT
from src.repository.call_repository import CallRepository
from src.service.audio_service import AudioService
from src.service.news_service import NewsService
from src.service.traffic_service import TrafficService


logger = logging.getLogger(__name__)


class PhoneAssistantNodes:
    def __init__(
        self,
        audio_service: AudioService,
        llm_client: LLMClient,
        news_service: NewsService,
        traffic_service: TrafficService,
        call_repository: CallRepository,
    ):
        self._audio_service = audio_service
        self._llm_client = llm_client
        self._news_service = news_service
        self._traffic_service = traffic_service
        self._call_repository = call_repository

    def download_recording(self, state: PhoneAssistantState) -> PhoneAssistantState:
        if state.record_url:
            state.user_audio_path = self._audio_service.download_recording(state.record_url)
            logger.info("Recording downloaded session_id=%s", state.session_id)
        return state

    def transcribe_audio(self, state: PhoneAssistantState) -> PhoneAssistantState:
        if state.user_audio_path:
            state.user_text = self._audio_service.transcribe_mp3(state.user_audio_path)
        if not state.user_text.strip():
            state.ai_text = "I'm sorry, I didn't catch that."
            logger.info("Transcription empty session_id=%s", state.session_id)
        return state

    def detect_intent(self, state: PhoneAssistantState) -> PhoneAssistantState:
        if state.ai_text:
            return state

        traffic_prompt = TRAFFIC_INTENT_PROMPT.format(user_text=state.user_text)
        traffic = self._llm_client.generate_structured(
            traffic_prompt,
            TrafficIntentOutput,
            TrafficIntentOutput(),
        )
        if traffic.intent == TrafficIntent.TRAFFIC:
            state.intent = TrafficIntent.TRAFFIC.value
            state.traffic_start = traffic.start
            state.traffic_end = traffic.end
            logger.info("Traffic intent selected session_id=%s", state.session_id)
            return state

        intent_prompt = ASSISTANT_INTENT_PROMPT.format(user_text=state.user_text)
        assistant_intent = self._llm_client.generate_structured(
            intent_prompt,
            AssistantIntentOutput,
            AssistantIntentOutput(),
        )
        state.intent = assistant_intent.intent.value
        logger.info("Assistant intent selected session_id=%s intent=%s", state.session_id, state.intent)
        return state

    def handle_traffic(self, state: PhoneAssistantState) -> PhoneAssistantState:
        state.ai_text = self._traffic_service.get_traffic_time(state.traffic_start, state.traffic_end)
        logger.info("Traffic response generated session_id=%s", state.session_id)
        return state

    def handle_news(self, state: PhoneAssistantState) -> PhoneAssistantState:
        state.ai_text = self._news_service.get_tamil_nadu_news()
        logger.info("News response generated session_id=%s", state.session_id)
        return state

    def handle_general_chat(self, state: PhoneAssistantState) -> PhoneAssistantState:
        try:
            language = detect(state.user_text)
        except Exception:
            language = "en"

        language_instruction = "Reply in Tamil." if language == "ta" else "Reply in English."
        prompt = GENERAL_ASSISTANT_PROMPT.format(
            language_instruction=language_instruction,
            user_text=state.user_text,
        )
        state.ai_text = self._llm_client.generate_text(prompt) or "Sorry I am facing technical issues."
        logger.info("General chat response generated session_id=%s language=%s", state.session_id, language)
        return state

    def generate_tts(self, state: PhoneAssistantState) -> PhoneAssistantState:
        state.ai_audio_file = self._audio_service.generate_tts(state.ai_text)
        logger.info("TTS generated session_id=%s audio_file=%s", state.session_id, state.ai_audio_file)
        return state

    def persist_turn(self, state: PhoneAssistantState) -> PhoneAssistantState:
        self._call_repository.add_call_turn(
            session_id=state.session_id,
            user_text=state.user_text,
            ai_text=state.ai_text,
            user_audio=state.user_audio_path,
            ai_audio=state.ai_audio_file,
        )
        logger.info("Call turn persisted session_id=%s", state.session_id)
        return state

    def check_end_call(self, state: PhoneAssistantState) -> PhoneAssistantState:
        state.should_end_call = "bye" in state.user_text.lower()
        if state.should_end_call:
            self._call_repository.end_call_session(state.session_id)
            logger.info("End call detected session_id=%s", state.session_id)
        return state


def route_intent(state: PhoneAssistantState) -> str:
    if state.ai_text:
        return "generate_tts"
    if state.intent == TrafficIntent.TRAFFIC.value:
        return "traffic"
    if state.intent == AssistantIntent.TAMIL_NADU_NEWS.value:
        return "news"
    return "general_chat"
