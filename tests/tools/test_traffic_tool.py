from src.exception.exceptions import ExternalServiceException
from src.tools.traffic_tool import TrafficTool


class TestGeocoder:
    __test__ = False

    def __init__(self, value):
        self.value = value

    def get_coordinates(self, place):
        return self.value


class TestTraffic:
    __test__ = False

    def get_travel_minutes(self, start, end):
        return 12


class BrokenGeocoder:
    def get_coordinates(self, place):
        raise ExternalServiceException("broken")


def test_traffic_tool_returns_not_found_when_location_missing():
    text = TrafficTool(TestGeocoder(None), TestTraffic()).get_traffic_time("A", "B")

    assert "couldn't find" in text


def test_traffic_tool_returns_minutes():
    text = TrafficTool(TestGeocoder([1, 2]), TestTraffic()).get_traffic_time("A", "B")

    assert "12 minutes" in text


def test_traffic_tool_handles_provider_failure():
    text = TrafficTool(BrokenGeocoder(), TestTraffic()).get_traffic_time("A", "B")

    assert "couldn't get traffic" in text
