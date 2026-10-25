from typing import Any, Dict
from src.client.ytdlp_client import YtDlpClient


class YouTubeTool:
    """Tool encapsulating YouTube audio streaming resolution."""

    def __init__(self, ytdlp_client: YtDlpClient):
        self.ytdlp_client = ytdlp_client

    async def execute(self, query: str, language: str = "en") -> Dict[str, Any]:
        """Resolves stream URL for live ffmpeg piping."""
        clean_query = query.replace("play", "").replace("song", "").replace("music", "").strip()
        stream_url = await self.ytdlp_client.get_audio_stream_url(clean_query)

        if stream_url:
            spoken_ack = (
                f"கண்டிப்பாக, {clean_query} பாடலை இசைக்கிறேன்."
                if language == "ta"
                else f"Sure, playing {clean_query} for you now."
            )
            return {
                "tool_name": "youtube_tool",
                "stream_url": stream_url,
                "spoken_output": spoken_ack,
                "status": "ready_to_stream",
            }
        else:
            fallback = (
                "மன்னிக்கவும், அந்த ஆடியோவை எடுக்க முடியவில்லை."
                if language == "ta"
                else "I'm sorry, I couldn't load that audio stream right now."
            )
            return {
                "tool_name": "youtube_tool",
                "stream_url": None,
                "spoken_output": fallback,
                "status": "failed",
            }
