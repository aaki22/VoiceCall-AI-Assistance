from src.models.intent import AssistantIntent, AssistantIntentOutput, TrafficIntent, TrafficIntentOutput


def test_traffic_intent_defaults_to_other():
    output = TrafficIntentOutput()

    assert output.intent == TrafficIntent.OTHER
    assert output.start == ""
    assert output.end == ""


def test_assistant_intent_validates_known_value():
    output = AssistantIntentOutput.model_validate({"intent": "tamil_nadu_news"})

    assert output.intent == AssistantIntent.TAMIL_NADU_NEWS
