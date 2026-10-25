import logging

import requests

from src.exception.exceptions import ExternalServiceException


logger = logging.getLogger(__name__)


class RecordingClient:
    def __init__(self, auth_id: str, auth_token: str, timeout_seconds: float):
        self._auth_id = auth_id
        self._auth_token = auth_token
        self._timeout_seconds = timeout_seconds

    def download(self, record_url: str) -> bytes:
        try:
            response = requests.get(
                record_url,
                headers={"X-Auth-ID": self._auth_id, "X-Auth-Token": self._auth_token},
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()
            return response.content
        except Exception as exc:
            logger.exception("Recording download failed")
            raise ExternalServiceException("Recording download failed") from exc
