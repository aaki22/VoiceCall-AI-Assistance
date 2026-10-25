import base64
import logging

import requests

from src.exception.exceptions import ExternalServiceException


logger = logging.getLogger(__name__)


class InworldTTSClient:
    def __init__(
        self,
        url: str,
        auth_token: str,
        voice_id: str,
        model_id: str,
        timeout_seconds: float,
    ):
        self._url = url
        self._auth_token = auth_token
        self._voice_id = voice_id
        self._model_id = model_id
        self._timeout_seconds = timeout_seconds

    def synthesize_mp3(self, text: str) -> bytes:
        try:
            response = requests.post(
                self._url,
                json={"text": text, "voiceId": self._voice_id, "modelId": self._model_id},
                headers={
                    "Authorization": f"Basic {self._auth_token}",
                    "Content-Type": "application/json",
                },
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()
            return base64.b64decode(response.json()["audioContent"])
        except Exception as exc:
            logger.exception("TTS request failed")
            raise ExternalServiceException("TTS request failed") from exc
