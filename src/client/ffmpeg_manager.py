import asyncio
import os
import signal
from typing import AsyncGenerator, Optional
from src.utils.logger import logger


class FFmpegManager:
    """Manages ffmpeg streaming subprocesses with POSIX process group lifecycle management."""

    def __init__(self, target_sample_rate: int = 8000):
        self.target_sample_rate = target_sample_rate
        self.chunk_size = 320  # 20ms frame = 160 samples * 2 bytes for 16-bit PCM

    async def stream_audio_pipe(
        self, stream_url: str
    ) -> AsyncGenerator[tuple[bytes, int], None]:
        """Pipes remote audio stream through ffmpeg transcoding directly to stdout.

        Yields (pcm_chunk, pid) for each 20ms frame.
        Uses process groups so the entire pipeline can be terminated in <300ms upon barge-in.
        """
        cmd = [
            "ffmpeg",
            "-re",  # Read input at native frame rate
            "-i",
            stream_url,
            "-f",
            "s16le",  # Signed 16-bit little-endian PCM
            "-ac",
            "1",  # Mono
            "-ar",
            str(self.target_sample_rate),
            "-loglevel",
            "quiet",
            "pipe:1",
        ]

        process: Optional[asyncio.subprocess.Process] = None
        try:
            # preexec_fn=os.setsid creates a new process group for clean signal handling
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
                preexec_fn=os.setsid if hasattr(os, "setsid") else None,
            )

            pid = process.pid
            assert process.stdout is not None

            while True:
                chunk = await process.stdout.read(self.chunk_size)
                if not chunk:
                    break
                yield chunk, pid

        except asyncio.CancelledError:
            if process and process.pid:
                self.terminate_process_group(process.pid)
            raise
        except Exception as e:
            logger.error(f"ffmpeg pipe streaming error: {e}")
        finally:
            if process and process.returncode is None:
                self.terminate_process_group(process.pid)

    @staticmethod
    def terminate_process_group(pid: int) -> bool:
        """Terminates an entire subprocess group immediately using SIGTERM and SIGKILL.

        Guarantees zero zombie processes (NFR-002).
        """
        try:
            pgid = os.getpgid(pid) if hasattr(os, "getpgid") else pid
            logger.info(f"Terminating subprocess group pgid={pgid} (pid={pid})")
            os.killpg(pgid, signal.SIGTERM)
            return True
        except ProcessLookupError:
            # Process already terminated
            return True
        except Exception as e:
            logger.warning(f"Error terminating process group {pid}: {e}")
            try:
                os.kill(pid, signal.SIGKILL)
                return True
            except Exception:
                return False
