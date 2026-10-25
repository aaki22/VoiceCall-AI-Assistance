import pytest
from src.agents.call_orchestrator_graph import classify_intent, detect_language


def test_language_detection_tamil():
    """Verify Tamil script detection."""
    tamil_text = "வணக்கம் சென்னை ரயில் நேரம் சொல்லுங்க"
    lang = detect_language(tamil_text)
    assert lang == "ta"


def test_language_detection_tanglish():
    """Verify Tanglish code-switch keyword detection."""
    tanglish_text = "Chennai central ku train timings enna irukku sollunga"
    lang = detect_language(tanglish_text)
    assert lang == "tanglish"


def test_language_detection_english():
    """Verify English language detection."""
    english_text = "What is the price of iPhone 15 in India?"
    lang = detect_language(english_text)
    assert lang == "en"


def test_intent_classification():
    """Verify multi-domain intent routing."""
    assert classify_intent("Play MS Subbulakshmi song") == "youtube"
    assert classify_intent("Chennai to Madurai train timings") == "transit"
    assert classify_intent("Remind me to take medicine at 8 PM") == "reminder"
    assert classify_intent("Find nearest dental clinic in Adyar") == "maps"
    assert classify_intent("What is the cost of Samsung S24 on Flipkart?") == "search"
    assert classify_intent("Hello Theodore, good morning") == "general"
