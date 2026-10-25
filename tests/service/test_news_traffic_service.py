from src.service.news_service import NewsService
from src.service.traffic_service import TrafficService


class TestNewsTool:
    __test__ = False

    def __init__(self, headlines):
        self.headlines = headlines

    def get_tamil_nadu_headlines(self, limit):
        return self.headlines


class TestTrafficTool:
    __test__ = False

    def get_traffic_time(self, start_place, end_place):
        return f"{start_place}->{end_place}"


def test_news_service_formats_headlines():
    text = NewsService(TestNewsTool(["A", "B"])).get_tamil_nadu_news()

    assert "இன்றைய தமிழ்நாடு முக்கிய செய்திகள்" in text
    assert "1. A." in text


def test_news_service_handles_empty_headlines():
    assert NewsService(TestNewsTool([])).get_tamil_nadu_news() == "இப்போது புதிய செய்திகள் இல்லை."


def test_traffic_service_delegates_to_tool():
    assert TrafficService(TestTrafficTool()).get_traffic_time("A", "B") == "A->B"
