from src.client.geocoding_client import GeocodingClient
from src.client.traffic_client import TrafficClient
from src.exception.exceptions import ExternalServiceException


class TrafficTool:
    def __init__(self, geocoding_client: GeocodingClient, traffic_client: TrafficClient):
        self._geocoding_client = geocoding_client
        self._traffic_client = traffic_client

    def get_traffic_time(self, start_place: str, end_place: str) -> str:
        try:
            start_coords = self._geocoding_client.get_coordinates(start_place)
            end_coords = self._geocoding_client.get_coordinates(end_place)
            if not start_coords or not end_coords:
                return "Sorry, I couldn't find that location."
            minutes = self._traffic_client.get_travel_minutes(start_coords, end_coords)
            return f"Current travel time from {start_place} to {end_place} is about {minutes} minutes."
        except ExternalServiceException:
            return "Sorry, I couldn't get traffic information."
