from src.prompts.assistant_prompts import GENERAL_ASSISTANT_PROMPT


def test_general_assistant_prompt_renders_user_text():
    prompt = GENERAL_ASSISTANT_PROMPT.format(language_instruction="Reply in English.", user_text="hello")

    assert "hello" in prompt
    assert "Reply in English." in prompt
