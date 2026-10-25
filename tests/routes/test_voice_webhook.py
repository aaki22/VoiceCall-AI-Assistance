from src.service.conversation_service import build_record_xml


def test_build_record_xml_contains_provider_record_instruction():
    xml = build_record_xml("session-1")

    assert "<Record" in xml
    assert "session_id=session-1" in xml
    assert 'method="POST"' in xml
