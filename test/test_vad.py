import pytest
from src.utils.vad import VoiceActivityDetector


def test_vad_silence_detection():
    """Test that silence does not trigger speech or barge-in."""
    vad = VoiceActivityDetector(sample_rate=8000, frame_ms=20, speech_energy_threshold=300.0)
    silent_frame = b"\x00" * 320  # 20ms silence

    is_turn_done, is_barge_in, completed_pcm = vad.process_frame(silent_frame, is_system_streaming_audio=False)
    assert not is_turn_done
    assert not is_barge_in
    assert completed_pcm is None


def test_vad_speech_turn_boundary_at_600ms():
    """Test that after speech, 600ms of silence completes the turn (hangover threshold)."""
    vad = VoiceActivityDetector(
        sample_rate=8000,
        frame_ms=20,
        speech_energy_threshold=100.0,
        silence_hangover_ms=600,
    )
    # Generate high energy simulated speech frame
    speech_frame = b"\x50\x20" * 160  # high RMS audio samples
    silent_frame = b"\x00" * 320

    # 1. Caller speaks for 3 frames (60ms)
    for _ in range(3):
        is_turn_done, _, _ = vad.process_frame(speech_frame, is_system_streaming_audio=False)
        assert not is_turn_done
    assert vad.is_speaking

    # 2. Caller goes silent for 29 frames (580ms) -> Still waiting for 600ms threshold
    for _ in range(29):
        is_turn_done, _, _ = vad.process_frame(silent_frame, is_system_streaming_audio=False)
        assert not is_turn_done

    # 3. 30th silent frame reaches exactly 600ms -> Turn completed!
    is_turn_done, _, completed_pcm = vad.process_frame(silent_frame, is_system_streaming_audio=False)
    assert is_turn_done
    assert completed_pcm is not None
    assert len(completed_pcm) > 0


def test_vad_barge_in_detection_at_200ms():
    """Test that sustained voice energy during system audio playback triggers barge-in in >=200ms."""
    vad = VoiceActivityDetector(
        sample_rate=8000,
        frame_ms=20,
        speech_energy_threshold=100.0,
        barge_in_threshold_ms=200,
    )
    speech_frame = b"\x50\x20" * 160

    # 9 frames = 180ms of speech (below 200ms threshold)
    for _ in range(9):
        _, is_barge_in, _ = vad.process_frame(speech_frame, is_system_streaming_audio=True)
        assert not is_barge_in

    # 10th frame = 200ms of sustained speech -> Barge-in fires!
    _, is_barge_in, _ = vad.process_frame(speech_frame, is_system_streaming_audio=True)
    assert is_barge_in
