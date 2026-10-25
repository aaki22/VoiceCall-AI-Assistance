from src.models.graph_state import PhoneAssistantState


def test_graph_state_has_safe_defaults():
    state = PhoneAssistantState(session_id="abc")

    assert state.intent == "general_chat"
    assert state.should_end_call is False
    assert state.metadata == {}
