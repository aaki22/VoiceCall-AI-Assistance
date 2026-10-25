from langgraph.graph import END, StateGraph

from src.agents.phone_assistant_nodes import PhoneAssistantNodes, route_intent
from src.models.graph_state import PhoneAssistantState


class PhoneAssistantGraph:
    def __init__(self, nodes: PhoneAssistantNodes):
        self._graph = self._build_graph(nodes)

    def run_turn(self, state: PhoneAssistantState) -> PhoneAssistantState:
        result = self._graph.invoke(state)
        if isinstance(result, PhoneAssistantState):
            return result
        return PhoneAssistantState.model_validate(result)

    def _build_graph(self, nodes: PhoneAssistantNodes):
        graph = StateGraph(PhoneAssistantState)
        graph.add_node("download_recording", nodes.download_recording)
        graph.add_node("transcribe_audio", nodes.transcribe_audio)
        graph.add_node("detect_intent", nodes.detect_intent)
        graph.add_node("handle_traffic", nodes.handle_traffic)
        graph.add_node("handle_news", nodes.handle_news)
        graph.add_node("handle_general_chat", nodes.handle_general_chat)
        graph.add_node("generate_tts", nodes.generate_tts)
        graph.add_node("persist_turn", nodes.persist_turn)
        graph.add_node("check_end_call", nodes.check_end_call)

        graph.set_entry_point("download_recording")
        graph.add_edge("download_recording", "transcribe_audio")
        graph.add_edge("transcribe_audio", "detect_intent")
        graph.add_conditional_edges(
            "detect_intent",
            route_intent,
            {
                "traffic": "handle_traffic",
                "news": "handle_news",
                "general_chat": "handle_general_chat",
                "generate_tts": "generate_tts",
            },
        )
        graph.add_edge("handle_traffic", "generate_tts")
        graph.add_edge("handle_news", "generate_tts")
        graph.add_edge("handle_general_chat", "generate_tts")
        graph.add_edge("generate_tts", "persist_turn")
        graph.add_edge("persist_turn", "check_end_call")
        graph.add_edge("check_end_call", END)
        return graph.compile()
