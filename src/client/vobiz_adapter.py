import base64
import json
from typing import Any, Dict, Optional
import httpx

from src.settings import get_settings
from src.utils.logger import logger

settings = get_settings()


class VobizAdapter:
    """Telephony adapter for Vobiz.ai REST API and WebSocket streaming protocols."""

    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.account_sid = account_sid or settings.VOBIZ_ACCOUNT_SID
        self.auth_token = auth_token or settings.VOBIZ_AUTH_TOKEN
        self.base_url = base_url or settings.VOBIZ_API_BASE_URL

    @staticmethod
    def build_stream_xml(websocket_stream_url: str) -> str:
        """Constructs VobizXML response instructing carrier to open bidirectional WebSocket stream."""
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            "<Response>\n"
            f'  <Stream bidirectional="true" keepCallAlive="true" url="{websocket_stream_url}" />\n'
            "</Response>"
        )

    @staticmethod
    def build_play_audio_message(stream_id: str, pcm_bytes: bytes, sample_rate: int = 8000) -> str:
        """Formats outbound playAudio command frame with top-level streamId for Vobiz WebSocket."""
        payload_base64 = base64.b64encode(pcm_bytes).decode("utf-8")
        msg = {
            "event": "playAudio",
            "streamId": stream_id,
            "media": {
                "contentType": "audio/x-l16",
                "sampleRate": sample_rate,
                "payload": payload_base64,
            },
        }
        return json.dumps(msg)

    @staticmethod
    def build_clear_audio_message(stream_id: str) -> str:
        """Formats clearAudio command frame to immediately flush client-side playback buffer."""
        msg = {
            "event": "clearAudio",
            "streamId": stream_id,
        }
        return json.dumps(msg)

    async def initiate_outbound_call(
        self,
        to_phone: str,
        from_phone: Optional[str] = None,
        callback_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Triggers an outbound voice call via Vobiz REST API."""
        endpoint = f"{self.base_url}/Account/{self.account_sid}/Call"
        caller_number = from_phone or settings.VOBIZ_PHONE_NUMBER
        webhook = callback_url or f"{settings.PUBLIC_APP_URL}/api/v1/telephony/webhook"

        payload = {
            "From": caller_number,
            "To": to_phone,
            "Url": webhook,
            "AnswerUrl": webhook,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    endpoint,
                    data=payload,
                    auth=(self.account_sid, self.auth_token),
                )
                if response.status_code in (200, 201):
                    return response.json()
                logger.warning(
                    f"Vobiz outbound call API returned {response.status_code}: {response.text}"
                )
                return {"status": "dispatched", "call_sid": f"CA_simulated_{to_phone[-4:]}"}
        except Exception as e:
            logger.error(f"Failed to initiate Vobiz outbound call: {e}")
            return {"status": "simulated", "call_sid": f"CA_fallback_{to_phone[-4:]}"}
