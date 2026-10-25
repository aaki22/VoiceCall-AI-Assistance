from src.tools.news_tool import NewsTool


class NewsService:
    def __init__(self, news_tool: NewsTool):
        self._news_tool = news_tool

    def get_tamil_nadu_news(self) -> str:
        headlines = self._news_tool.get_tamil_nadu_headlines(limit=3)
        if not headlines:
            return "இப்போது புதிய செய்திகள் இல்லை."
        news_text = "இன்றைய தமிழ்நாடு முக்கிய செய்திகள்: "
        return news_text + " ".join(f"{index}. {headline}." for index, headline in enumerate(headlines, 1))
