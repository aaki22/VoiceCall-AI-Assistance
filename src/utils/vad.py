import math
import struct
from typing import List, Optional, Tuple


class VoiceActivityDetector:
    """Voice Activity Detection (VAD) and turn-taking state machine for 8kHz 16-bit PCM telephony streams.

    Features:
    - Analyzes 20ms audio frames (160 samples per frame).
    - RMS energy calculation with adaptive noise floor.
    - 600ms silence hangover window for end-of-speech (EOS) turn locking.
    - 200ms sustained speech threshold for instant barge-in cutoff during playback.
    """

    def __init__(
        self,
        sample_rate: int = 8000,
        frame_ms: int = 20,
        speech_energy_threshold: float = 350.0,
        silence_hangover_ms: int = 600,
        barge_in_threshold_ms: int = 200,
    ):
        self.sample_rate = sample_rate
        self.frame_ms = frame_ms
        self.samples_per_frame = int(sample_rate * (frame_ms / 1000.0))
        self.bytes_per_frame = self.samples_per_frame * 2  # 16-bit PCM = 2 bytes per sample

        self.speech_energy_threshold = speech_energy_threshold
        self.silence_hangover_ms = silence_hangover_ms
        self.barge_in_threshold_ms = barge_in_threshold_ms

        # State tracking
        self.is_speaking = False
        self.current_silence_duration_ms = 0
        self.consecutive_speech_duration_ms = 0
        self.accumulated_utterance_frames: List[bytes] = []

    def calculate_frame_rms(self, frame_bytes: bytes) -> float:
        """Calculates Root Mean Square (RMS) audio energy for a raw 16-bit PCM frame."""
        if len(frame_bytes) < 2:
            return 0.0

        sample_count = len(frame_bytes) // 2
        # Unpack as little-endian signed 16-bit shorts ('<h')
        samples = struct.unpack(f"<{sample_count}h", frame_bytes[: sample_count * 2])

        sum_squares = sum(s * s for s in samples)
        rms = math.sqrt(sum_squares / sample_count) if sample_count > 0 else 0.0
        return rms

    def process_frame(
        self, frame_bytes: bytes, is_system_streaming_audio: bool = False
    ) -> Tuple[bool, bool, Optional[bytes]]:
        """Processes a single 20ms PCM audio frame.

        Args:
            frame_bytes: Raw 16-bit linear PCM bytes (expected 320 bytes for 20ms @ 8kHz).
            is_system_streaming_audio: True if the assistant/system is currently playing or streaming audio.

        Returns:
            Tuple of:
            - is_turn_completed (bool): True if caller finished speaking (>600ms silence).
            - is_barge_in_detected (bool): True if caller interrupted active playback (>200ms speech).
            - completed_utterance (Optional[bytes]): Concatenated PCM bytes if turn completed, else None.
        """
        rms = self.calculate_frame_rms(frame_bytes)
        is_speech_frame = rms > self.speech_energy_threshold

        is_turn_completed = False
        is_barge_in_detected = False
        completed_utterance: Optional[bytes] = None

        if is_speech_frame:
            self.consecutive_speech_duration_ms += self.frame_ms
            self.current_silence_duration_ms = 0

            if not self.is_speaking:
                self.is_speaking = True

            self.accumulated_utterance_frames.append(frame_bytes)

            # Check for Barge-in during active system playback
            if is_system_streaming_audio and self.consecutive_speech_duration_ms >= self.barge_in_threshold_ms:
                is_barge_in_detected = True

        else:
            # Silence / Noise floor frame
            self.consecutive_speech_duration_ms = 0

            if self.is_speaking:
                self.accumulated_utterance_frames.append(frame_bytes)
                self.current_silence_duration_ms += self.frame_ms

                # Check for Turn-Taking boundary (>600ms hangover)
                if self.current_silence_duration_ms >= self.silence_hangover_ms:
                    is_turn_completed = True
                    completed_utterance = b"".join(self.accumulated_utterance_frames)
                    self.reset_turn()

        return is_turn_completed, is_barge_in_detected, completed_utterance

    def reset_turn(self) -> None:
        """Resets speech accumulation counters for the next turn."""
        self.is_speaking = False
        self.current_silence_duration_ms = 0
        self.consecutive_speech_duration_ms = 0
        self.accumulated_utterance_frames.clear()
