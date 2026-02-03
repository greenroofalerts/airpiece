"""Text-to-speech using Piper — runs locally on the Pi, outputs to Bluetooth earpiece."""

import io
import subprocess
import logging
import wave
from config import PIPER_MODEL, TTS_SPEED

log = logging.getLogger(__name__)


def speak(text: str):
    """Convert text to speech and play through the default audio output (Bluetooth earpiece)."""
    try:
        # Piper outputs raw WAV to stdout
        result = subprocess.run(
            [
                "piper",
                "--model", PIPER_MODEL,
                "--length-scale", str(1.0 / TTS_SPEED),
                "--output_file", "-",
            ],
            input=text.encode("utf-8"),
            capture_output=True,
            timeout=30,
        )

        if result.returncode != 0:
            log.error("Piper TTS failed: %s", result.stderr.decode())
            return

        # Play the WAV audio through aplay (ALSA)
        subprocess.run(
            ["aplay", "-q", "-"],
            input=result.stdout,
            timeout=30,
        )

    except FileNotFoundError:
        log.warning("Piper not installed — falling back to espeak")
        _speak_espeak(text)
    except subprocess.TimeoutExpired:
        log.error("TTS timed out")


def _speak_espeak(text: str):
    """Fallback TTS using espeak (pre-installed on most Pi OS)."""
    try:
        subprocess.run(
            ["espeak", "-v", "en-gb", "-s", "160", text],
            timeout=30,
        )
    except Exception as e:
        log.error("espeak fallback failed: %s", e)


def speak_confirmation(action: str):
    """Short confirmation beep/phrase."""
    speak(action)
