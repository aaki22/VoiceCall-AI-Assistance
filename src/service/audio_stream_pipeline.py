import asyncio
from typing import AsyncGenerator, Optional
from src.client.ffmpeg_manager import FFmpegManager
from src.utils.logger import logger


class AudioStreamPipeline:
    """Manages active streaming audio pipes and subprocess process groups."""

    def __init__(self):
        self.ffmpeg_manager = FFmpegManager(target_sample_rate=8000)
        self.active_pids: set[int] = set()

    async def pipe_stream_to_telephony(
        self, stream_url: str
    ) -> AsyncGenerator[bytes, None]:
        """Pipes raw 8kHz PCM chunks from ffmpeg to caller socket.

        Records PID so barge-in cutoff can terminate process in <300ms.
        """
        async for chunk, pid in self.ffmpeg_manager.stream_audio_pipe(stream_url):
            self.active_pids.add(pid)
            yield chunk

    def terminate_active_streams(self, pid: Optional[int] = None) -> int:
        """Terminates active media streaming subprocesses immediately.

        Returns count of terminated processes.
        """
        count = 0
        pids_to_kill = [pid] if pid else list(self.active_pids)

        for p in pids_to_kill:
            success = self.ffmpeg_manager.terminate_process_group(p)
            if success:
                count += 1
            self.active_pids.discard(p)

        logger.info(f"Terminated {count} streaming audio subprocesses on barge-in")
        return count
