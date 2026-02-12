"""AI integrations — Claude Vision for scene analysis, Whisper for STT."""

import base64
import logging
import tempfile
from pathlib import Path

import anthropic
from config import (
    ANTHROPIC_API_KEY,
    VISION_MODEL,
    VISION_MAX_TOKENS,
)

log = logging.getLogger(__name__)

# --- Claude Vision ---

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are Airpiece, a hands-free AI assistant mounted on a hard hat.
You help with green roof site surveys. You can see through a camera on the user's head.

Guidelines:
- Be concise. Your responses are read aloud through an earpiece while the user is working.
- Keep answers to 1-3 sentences unless asked for detail.
- When logging observations, confirm what you see and the note.
- For plant/species ID, give common name first, then latin name.
- For safety hazards, be direct and specific about the risk.
- You have access to GPS coordinates and timestamps for geolocation."""


def analyse_scene(image_b64: str, user_query: str, context: str = "") -> str:
    """Send a camera frame + user query to Claude Vision. Returns text response."""
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_b64,
                    },
                },
                {
                    "type": "text",
                    "text": f"{context}\n\nUser says: {user_query}" if context else user_query,
                },
            ],
        }
    ]

    try:
        response = client.messages.create(
            model=VISION_MODEL,
            max_tokens=VISION_MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=messages,
        )
        return response.content[0].text
    except Exception as e:
        log.error("Claude Vision API error: %s", e)
        return f"Sorry, I couldn't process that. Error: {e}"


def generate_report(events: list[dict]) -> str:
    """Generate a site survey report from today's logged events."""
    event_summary = "\n".join(
        f"- [{e['timestamp']}] ({e['event_type']}) {e.get('transcript', '')} → {e.get('ai_response', '')}"
        for e in events
    )

    response = client.messages.create(
        model=VISION_MODEL,
        max_tokens=2048,
        system="You are a technical report writer for green roof site surveys.",
        messages=[
            {
                "role": "user",
                "content": f"""Generate a concise site survey report from these logged events:

{event_summary}

Format: Summary, Key Findings (bulleted), Recommended Actions, Issues Noted.
Keep it professional and suitable for a client handover.""",
            }
        ],
    )
    return response.content[0].text


# --- Deepgram Speech-to-Text ---

def transcribe_audio(wav_bytes: bytes) -> str:
    """Transcribe WAV audio to text using Deepgram."""
    from deepgram import DeepgramClient, PrerecordedOptions
    from config import DEEPGRAM_API_KEY

    client = DeepgramClient(DEEPGRAM_API_KEY)

    options = PrerecordedOptions(
        model="nova-2",
        language="en-GB",
        smart_format=True,
    )

    try:
        response = client.listen.rest.v("1").transcribe_file(
            {"buffer": wav_bytes, "mimetype": "audio/wav"},
            options
        )
        return response.results.channels[0].alternatives[0].transcript.strip()
    except Exception as e:
        log.error("Deepgram STT error: %s", e)
        return ""
