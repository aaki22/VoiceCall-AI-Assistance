from pydantic import BaseModel


class CallTurnData(BaseModel):
    session_id: str
    user_text: str = ""
    ai_text: str = ""
    user_audio: str = ""
    ai_audio: str = ""


class RecordingDownload(BaseModel):
    record_url: str
    local_audio_path: str
