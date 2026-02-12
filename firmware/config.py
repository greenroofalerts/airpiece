"""Airpiece configuration — hardware pins, API keys, settings."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- API Keys ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY", "")

# --- Audio ---
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SIZE = 480  # 30ms frames at 16kHz (required by webrtcvad)
VAD_AGGRESSIVENESS = 2  # 0-3, higher = more aggressive filtering
SILENCE_TIMEOUT_SEC = 1.5  # seconds of silence before processing speech
WAKE_WORD = "airpiece"  # Porcupine wake word

# --- Camera ---
CAMERA_RESOLUTION = (1920, 1080)
CAMERA_FRAME_RATE = 15
JPEG_QUALITY = 85  # For frames sent to vision API

# --- GPS ---
GPS_SERIAL_PORT = "/dev/ttyAMA0"
GPS_BAUD_RATE = 9600

# --- TTS ---
PIPER_MODEL = "en_GB-alba-medium"  # British English voice
TTS_SPEED = 1.1  # Slightly faster than default

# --- Claude Vision ---
VISION_MODEL = "claude-sonnet-4-20250514"
VISION_MAX_TOKENS = 1024

# --- Paths ---
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "airpiece.db"
CAPTURES_DIR = DATA_DIR / "captures"
AUDIO_DIR = DATA_DIR / "audio"

# Ensure data dirs exist
DATA_DIR.mkdir(exist_ok=True)
CAPTURES_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(exist_ok=True)

# --- Logging ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
