import pytest

from src.exception.exceptions import ExternalServiceException
from src.tools.news_tool import NewsTool


class Entry:
    def __init__(self, title):
        self.title = title


class Feed:
    entries = [Entry("A"), Entry("B")]


def test_news_tool_returns_headlines(monkeypatch):
    monkeypatch.setattr("src.tools.news_tool.feedparser.parse", lambda url: Feed())

    assert NewsTool().get_tamil_nadu_headlines(limit=1) == ["A"]


def test_news_tool_raises_controlled_error(monkeypatch):
    monkeypatch.setattr("src.tools.news_tool.feedparser.parse", lambda url: (_ for _ in ()).throw(RuntimeError()))

    with pytest.raises(ExternalServiceException):
        NewsTool().get_tamil_nadu_headlines()
