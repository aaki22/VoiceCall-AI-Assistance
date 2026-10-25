import feedparser

from src.constants.providers import NEWS_RSS_URL
from src.exception.exceptions import ExternalServiceException


class NewsTool:
    def get_tamil_nadu_headlines(self, limit: int = 3) -> list[str]:
        try:
            feed = feedparser.parse(NEWS_RSS_URL)
            return [entry.title for entry in feed.entries[:limit]]
        except Exception as exc:
            raise ExternalServiceException("News feed request failed") from exc
