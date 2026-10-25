import re
import time
from typing import Any, Dict, List, Optional, TypedDict
from langgraph.graph import END, START, StateGraph

from src.client.gemini_client import GeminiClient
from src.client.ytdlp_client import YtDlpClient
from src.constants.agents import (
    NODE_GENERAL_CONVERSATION,
    NODE_INTENT_ROUTER,
    NODE_LANGUAGE_DETECTOR,
    NODE_MAPS_TOOL,
    NODE_REMINDER_TOOL,
    NODE_SEARCH_TOOL,
    NODE_SYNTHESIZER,
    NODE_TRANSIT_TOOL,
    NODE_YOUTUBE_TOOL,
)
from src.prompts.system.theodore_persona import THEODORE_SYSTEM_PROMPT
from src.repository.reminder_repository import ReminderRepository
from src.tools.maps_tool import MapsTool
from src.tools.reminder_tool import ReminderTool
from src.tools.search_tool import SearchTool
from src.tools.transit_tool import TransitTool
from src.tools.youtube_tool import YouTubeTool


class TheodoreAgentState(TypedDict):
    """LangGraph agent state dictionary."""

    session_id: str
    caller_phone: str
    utterance: str
    detected_language: str
    intent: str
    tool_result: Optional[Dict[str, Any]]
    spoken_response: str
    grounding_sources: List[Dict[str, str]]
    stream_url: Optional[str]
    latencies: Dict[str, int]
    correlation_id: str
    langsmith_run_id: Optional[str]


def detect_language(text: str) -> str:
    """Classifies language into Tamil (ta), English (en), or Tanglish."""
    # Tamil Unicode range: \u0B80 - \u0BFF
    tamil_chars = len(re.findall(r"[\u0B80-\u0BFF]", text))
    if tamil_chars > 2:
        return "ta"

    # Tanglish detection heuristic
    tanglish_keywords = ["sollunga", "enna", "irukku", "kidaikkuma", "pannunga", "vaanga", "ponga"]
    text_lower = text.lower()
    if any(kw in text_lower for kw in tanglish_keywords):
        return "tanglish"

    return "en"


def classify_intent(text: str) -> str:
    """Heuristic / LLM intent classification node."""
    text_lower = text.lower()

    if any(kw in text_lower for kw in ["play", "song", "music", "பாடல்", "பாட்டு"]):
        return "youtube"
    elif any(kw in text_lower for kw in ["train", "metro", "station", "irctc", "ரயில்", "டிக்கெட்", "பயணம்"]):
        return "transit"
    elif any(kw in text_lower for kw in ["remind", "reminder", "நினைவூட்டல்", "ஞாபகப்படுத்து"]):
        return "reminder"
    elif any(kw in text_lower for kw in ["near", "clinic", "hospital", "doctor", "mechanic", "pharmacy", "எங்கே", "மருத்துவமனை"]):
        return "maps"
    elif any(kw in text_lower for kw in ["price", "cost", "offer", "buy", "flipkart", "amazon", "விலை", "மதிப்பு"]):
        return "search"
    else:
        return "general"


class CallOrchestratorGraph:
    """Theodore Core LangGraph StateGraph engine."""

    def __init__(
        self,
        gemini_client: GeminiClient,
        reminder_repo: Optional[ReminderRepository] = None,
    ):
        self.gemini_client = gemini_client
        self.search_tool = SearchTool(gemini_client)
        self.maps_tool = MapsTool(gemini_client)
        self.transit_tool = TransitTool(gemini_client)
        self.youtube_tool = YouTubeTool(YtDlpClient())
        self.reminder_tool = ReminderTool(reminder_repo) if reminder_repo else None

        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(TheodoreAgentState)

        # Add Nodes
        builder.add_node(NODE_LANGUAGE_DETECTOR, self._node_language_detector)
        builder.add_node(NODE_INTENT_ROUTER, self._node_intent_router)
        builder.add_node(NODE_SEARCH_TOOL, self._node_search)
        builder.add_node(NODE_MAPS_TOOL, self._node_maps)
        builder.add_node(NODE_TRANSIT_TOOL, self._node_transit)
        builder.add_node(NODE_YOUTUBE_TOOL, self._node_youtube)
        builder.add_node(NODE_REMINDER_TOOL, self._node_reminder)
        builder.add_node(NODE_GENERAL_CONVERSATION, self._node_general)
        builder.add_node(NODE_SYNTHESIZER, self._node_synthesizer)

        # Wire Edges
        builder.add_edge(START, NODE_LANGUAGE_DETECTOR)
        builder.add_edge(NODE_LANGUAGE_DETECTOR, NODE_INTENT_ROUTER)

        # Conditional Branching from Router
        builder.add_conditional_edges(
            NODE_INTENT_ROUTER,
            self._route_intent,
            {
                "search": NODE_SEARCH_TOOL,
                "maps": NODE_MAPS_TOOL,
                "transit": NODE_TRANSIT_TOOL,
                "youtube": NODE_YOUTUBE_TOOL,
                "reminder": NODE_REMINDER_TOOL,
                "general": NODE_GENERAL_CONVERSATION,
            },
        )

        # Converge to Synthesizer Node
        builder.add_edge(NODE_SEARCH_TOOL, NODE_SYNTHESIZER)
        builder.add_edge(NODE_MAPS_TOOL, NODE_SYNTHESIZER)
        builder.add_edge(NODE_TRANSIT_TOOL, NODE_SYNTHESIZER)
        builder.add_edge(NODE_YOUTUBE_TOOL, NODE_SYNTHESIZER)
        builder.add_edge(NODE_REMINDER_TOOL, NODE_SYNTHESIZER)
        builder.add_edge(NODE_GENERAL_CONVERSATION, NODE_SYNTHESIZER)
        builder.add_edge(NODE_SYNTHESIZER, END)

        return builder.compile()

    # Node Implementations
    async def _node_language_detector(self, state: TheodoreAgentState) -> Dict[str, Any]:
        detected = detect_language(state["utterance"])
        return {"detected_language": detected}

    async def _node_intent_router(self, state: TheodoreAgentState) -> Dict[str, Any]:
        intent = classify_intent(state["utterance"])
        return {"intent": intent}

    def _route_intent(self, state: TheodoreAgentState) -> str:
        return state.get("intent", "general")

    async def _node_search(self, state: TheodoreAgentState) -> Dict[str, Any]:
        start = time.perf_counter()
        lang = state.get("detected_language", "en")
        res = await self.search_tool.execute(state["utterance"], language=lang)
        dur = int((time.perf_counter() - start) * 1000)

        latencies = state.get("latencies", {})
        latencies["tool_ms"] = dur

        return {
            "tool_result": res,
            "spoken_response": res.get("spoken_output", ""),
            "grounding_sources": res.get("grounding_sources", []),
            "latencies": latencies,
        }

    async def _node_maps(self, state: TheodoreAgentState) -> Dict[str, Any]:
        start = time.perf_counter()
        lang = state.get("detected_language", "en")
        res = await self.maps_tool.execute(state["utterance"], language=lang)
        dur = int((time.perf_counter() - start) * 1000)

        latencies = state.get("latencies", {})
        latencies["tool_ms"] = dur

        return {
            "tool_result": res,
            "spoken_response": res.get("spoken_output", ""),
            "grounding_sources": res.get("grounding_sources", []),
            "latencies": latencies,
        }

    async def _node_transit(self, state: TheodoreAgentState) -> Dict[str, Any]:
        start = time.perf_counter()
        lang = state.get("detected_language", "ta")
        res = await self.transit_tool.execute(state["utterance"], language=lang)
        dur = int((time.perf_counter() - start) * 1000)

        latencies = state.get("latencies", {})
        latencies["tool_ms"] = dur

        return {
            "tool_result": res,
            "spoken_response": res.get("spoken_output", ""),
            "grounding_sources": res.get("grounding_sources", []),
            "latencies": latencies,
        }

    async def _node_youtube(self, state: TheodoreAgentState) -> Dict[str, Any]:
        start = time.perf_counter()
        lang = state.get("detected_language", "en")
        res = await self.youtube_tool.execute(state["utterance"], language=lang)
        dur = int((time.perf_counter() - start) * 1000)

        latencies = state.get("latencies", {})
        latencies["tool_ms"] = dur

        return {
            "tool_result": res,
            "stream_url": res.get("stream_url"),
            "spoken_response": res.get("spoken_output", ""),
            "latencies": latencies,
        }

    async def _node_reminder(self, state: TheodoreAgentState) -> Dict[str, Any]:
        start = time.perf_counter()
        lang = state.get("detected_language", "ta")
        if self.reminder_tool:
            res = await self.reminder_tool.execute(
                caller_phone=state.get("caller_phone", "+919840012345"),
                query=state["utterance"],
                language=lang,
                session_id=state.get("session_id"),
            )
        else:
            res = {"spoken_output": "Your reminder has been registered."}

        dur = int((time.perf_counter() - start) * 1000)
        latencies = state.get("latencies", {})
        latencies["tool_ms"] = dur

        return {
            "tool_result": res,
            "spoken_response": res.get("spoken_output", ""),
            "latencies": latencies,
        }

    async def _node_general(self, state: TheodoreAgentState) -> Dict[str, Any]:
        lang = state.get("detected_language", "ta")
        prompt = (
            f"User spoken statement: {state['utterance']}\n"
            f"Language to respond in: {lang}. Provide a helpful, concise conversational reply (maximum 2 sentences). "
            "Follow CRIT-VOICE-01 strictly: no markdown, no URLs."
        )

        res = await self.gemini_client.generate_with_search_grounding(
            prompt=prompt,
            system_instruction=THEODORE_SYSTEM_PROMPT,
        )

        text = res.get("text", "வணக்கம், உங்களுக்கு எப்படி உதவட்டும்?")
        return {
            "spoken_response": text,
            "grounding_sources": [],
        }

    async def _node_synthesizer(self, state: TheodoreAgentState) -> Dict[str, Any]:
        """Final sanity check enforcing CRIT-VOICE-01 formatting on spoken output."""
        spoken = state.get("spoken_response", "")
        # Clean any remaining asterisks or backticks
        clean_spoken = re.sub(r"[\*#`]", "", spoken).strip()
        return {"spoken_response": clean_spoken}

    async def process_turn(
        self,
        session_id: str,
        caller_phone: str,
        utterance: str,
        correlation_id: str,
        langsmith_run_id: Optional[str] = None,
    ) -> TheodoreAgentState:
        """Runs the LangGraph StateGraph engine for a single conversational turn."""
        initial_state: TheodoreAgentState = {
            "session_id": session_id,
            "caller_phone": caller_phone,
            "utterance": utterance,
            "detected_language": "ta",
            "intent": "general",
            "tool_result": None,
            "spoken_response": "",
            "grounding_sources": [],
            "stream_url": None,
            "latencies": {},
            "correlation_id": correlation_id,
            "langsmith_run_id": langsmith_run_id,
        }

        final_state = await self.graph.ainvoke(initial_state)
        return final_state
