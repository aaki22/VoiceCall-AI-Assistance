from src.models.call import CallTurnData, RecordingDownload
from src.models.response import ApiResponse, ErrorDTO


def test_call_turn_data_defaults_optional_text():
    data = CallTurnData(session_id="s1")

    assert data.user_text == ""
    assert data.ai_audio == ""


def test_recording_download_contract():
    data = RecordingDownload(record_url="url", local_audio_path="audio/a.mp3")

    assert data.record_url == "url"


def test_api_response_error_contract():
    response = ApiResponse[None](
        success=False,
        message="failed",
        error=ErrorDTO(code="X", details="detail"),
    )

    assert response.error.code == "X"
