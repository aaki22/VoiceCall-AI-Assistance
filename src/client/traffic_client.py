import logging

import requests

from src.constants.providers import TRAFFIC_DIRECTIONS_URL
from src.exception.exceptions import ExternalServiceException


logger = logging.getLogger(__name__)


class TrafficClient:
    def __init__(self, api_key: str, timeout_seconds: float):
        self._api_key = api_key
        self._timeout_seconds = timeout_seconds

    def get_travel_minutes(self, start_coords: list[float], end_coords: list[float]) -> int:
        try:
            response = requests.post(
                TRAFFIC_DIRECTIONS_URL,
                json={"coordinates": [start_coords, end_coords]},
                headers={
                    "Authorization": self._api_key,
                    "Content-Type": "application/json",
                },
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()
            data = response.json()
            duration = data["routes"][0]["summary"]["duration"]
            return int(duration / 60)
        except Exception as exc:
            logger.exception("Traffic request failed")
            raise ExternalServiceException("Traffic request failed") from exc
