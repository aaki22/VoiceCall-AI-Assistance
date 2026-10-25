import asyncio
import base64
import json
import uuid
from typing import AsyncGenerator, Optional
import websockets

from src.settings import get_settings
from src.utils.logger import logger

settings = get_settings()


class InworldTTSClient:
    """Inworld AI TTS-2 Flash low-latency streaming client over WebSockets."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        voice_id: Optional[str] = None,
        model_id: Optional[str] = None,
    ):
        self.api_key = api_key or settings.INWORLD_API_KEY
        self.voice_id = voice_id or settings.INWORLD_VOICE_ID
        self.model_id = model_id or settings.INWORLD_MODEL_ID
        self.ws_url = settings.INWORLD_WS_URL

    async def stream_speech(self, text: str) -> AsyncGenerator[bytes, None]:
        """Streams audio chunks for spoken text over Inworld WebSocket.

        Yields raw audio chunks as they arrive from Inworld AI.
        """
        # If API key is not configured or dummy, fallback to simulated PCM chunks
        if not self.api_key or self.api_key == "dummy_inworld_key":
            async for chunk in self._simulate_fallback_pcm_chunks(text):
                yield chunk
            return

        headers = {"Authorization": f"Basic {self.api_key}"}
        context_id = f"ctx-{uuid.uuid4().hex[:8]}"

        try:
            async with websockets.connect(self.ws_url, additional_headers=headers) as ws:
                # 1. Create context
                await ws.send(
                    json.dumps({
                        "type": "create",
                        "contextId": context_id,
                        "modelId": self.model_id,
                        "voiceId": self.voice_id,
                        "autoMode": True,
                    })
                )

                # 2. Send text payload
                await ws.send(
                    json.dumps({
                        "type": "send_text",
                        "contextId": context_id,
                        "text": text,
                    })
                )

                # 3. Close context
                await ws.send(
                    json.dumps({
                        "type": "close_context",
                        "contextId": context_id,
                    })
                )

                # 4. Stream response audio chunks
                async for message in ws:
                    payload = json.loads(message)
                    if "error" in payload:
                        logger.error(f"Inworld TTS error: {payload['error']}")
                        break

                    if "audioContent" in payload:
                        audio_chunk = base64.b64decode(payload["audioContent"])
                        yield audio_chunk

                    if payload.get("type") == "context_closed":
                        break
        except Exception as e:
            logger.warning(f"Inworld WebSocket streaming failed: {e}. Falling back to simulated PCM.")
            async for chunk in self._simulate_fallback_pcm_chunks(text):
                yield chunk

    async def _simulate_fallback_pcm_chunks(self, text: str) -> AsyncGenerator[bytes, None]:
        """Generates dummy 8kHz 16-bit PCM chunks for offline testing and fallback."""
        # 20ms frame at 8kHz 16-bit mono = 320 bytes
        frame_chunk = b"\x00" * 320
        # Yield approx 10 frames (~200ms audio)
        for _ in range(10):
            yield frame_chunk
            await asyncio.sleep(0.02)
