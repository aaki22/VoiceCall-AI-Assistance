from src.prompts.intent_prompts import ASSISTANT_INTENT_PROMPT, TRAFFIC_INTENT_PROMPT


def test_intent_prompts_render_user_text():
    assert "hello" in TRAFFIC_INTENT_PROMPT.format(user_text="hello")
    assert "hello" in ASSISTANT_INTENT_PROMPT.format(user_text="hello")
