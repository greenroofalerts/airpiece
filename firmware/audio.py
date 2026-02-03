"""Audio capture, voice activity detection, and wake word detection."""

import io
import wave
import logging
import struct
import pyaudio
import webrtcvad
from config import (
    SAMPLE_RATE,
    CHANNELS,
    CHUNK_SIZE,
    VAD_AGGRESSIVENESS,
    SILENCE_TIMEOUT_SEC,
)

log = logging.getLogger(__name__)


class AudioCapture:
    """Captures audio from the INMP441 I2S mic via ALSA/PyAudio."""

    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)
        self.stream = None

    def start(self):
        """Open the audio input stream."""
        self.stream = self.pa.open(
            format=pyaudio.paInt16,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE,
        )
        log.info("Audio stream opened (rate=%d, chunk=%d)", SAMPLE_RATE, CHUNK_SIZE)

    def stop(self):
        """Close the audio stream."""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.pa.terminate()
        log.info("Audio stream closed")

    def read_chunk(self) -> bytes:
        """Read a single chunk of audio data."""
        return self.stream.read(CHUNK_SIZE, exception_on_overflow=False)

    def is_speech(self, chunk: bytes) -> bool:
        """Check if an audio chunk contains speech using VAD."""
        try:
            return self.vad.is_speech(chunk, SAMPLE_RATE)
        except Exception:
            return False

    def listen_for_speech(self) -> bytes | None:
        """
        Block until speech is detected, then record until silence.
        Returns WAV audio bytes, or None if nothing meaningful captured.
        """
        frames = []
        silent_chunks = 0
        max_silent = int(SILENCE_TIMEOUT_SEC / (CHUNK_SIZE / SAMPLE_RATE))
        recording = False
        min_speech_chunks = 10  # ~300ms minimum to avoid false triggers

        log.debug("Listening for speech...")

        while True:
            chunk = self.read_chunk()

            if self.is_speech(chunk):
                if not recording:
                    log.debug("Speech detected, recording...")
                    recording = True
                frames.append(chunk)
                silent_chunks = 0
            elif recording:
                frames.append(chunk)
                silent_chunks += 1
                if silent_chunks >= max_silent:
                    break

        if len(frames) < min_speech_chunks:
            log.debug("Too short, ignoring (%d chunks)", len(frames))
            return None

        return self._frames_to_wav(frames)

    def _frames_to_wav(self, frames: list[bytes]) -> bytes:
        """Convert raw PCM frames to WAV format."""
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(b"".join(frames))
        return buf.getvalue()
