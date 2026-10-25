import asyncio
from typing import Optional
from src.utils.logger import logger


class YtDlpClient:
    """Wrapper for yt-dlp audio stream URL extraction."""

    async def get_audio_stream_url(self, search_query_or_url: str) -> Optional[str]:
        """Resolves direct stream URL using yt-dlp without downloading media to disk."""
        target = (
            search_query_or_url
            if search_query_or_url.startswith(("http://", "https://"))
            else f"ytsearch1:{search_query_or_url}"
        )

        cmd = [
            "yt-dlp",
            "-g",  # Get URL only
            "-f",
            "bestaudio",
            "--no-playlist",
            "--quiet",
            target,
        ]

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0 and stdout:
                stream_url = stdout.decode().strip().split("\n")[0]
                return stream_url
            else:
                logger.warning(f"yt-dlp failed to extract stream URL: {stderr.decode()}")
                return None
        except Exception as e:
            logger.error(f"Error executing yt-dlp subprocess: {e}")
            return None
