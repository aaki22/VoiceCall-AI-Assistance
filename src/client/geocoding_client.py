import logging

import requests

from src.constants.providers import NOMINATIM_USER_AGENT
from src.exception.exceptions import ExternalServiceException


logger = logging.getLogger(__name__)


class GeocodingClient:
    def __init__(self, timeout_seconds: float):
        self._timeout_seconds = timeout_seconds

    def get_coordinates(self, place: str) -> list[float] | None:
        try:
            response = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": place, "format": "json", "limit": 1},
                headers={"User-Agent": NOMINATIM_USER_AGENT},
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()
            data = response.json()
            if not data:
                return None
            return [float(data[0]["lon"]), float(data[0]["lat"])]
        except Exception as exc:
            logger.exception("Geocoding request failed place=%s", place)
            raise ExternalServiceException("Geocoding request failed") from exc
