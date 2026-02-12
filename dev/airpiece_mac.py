#!/usr/bin/env python3
"""
Airpiece Mac Dev Prototype
Voice → Webcam capture → Claude Vision → TTS response
"""

import os
import sys
import base64
import subprocess
import time
import io
import wave
import requests
import numpy as np
import sounddevice as sd
import cv2
from anthropic import Anthropic

# Config
SAMPLE_RATE = 16000
SILENCE_THRESHOLD = 0.02
SILENCE_DURATION = 1.5
MIN_SPEECH_DURATION = 0.5

anthropic = Anthropic()


def record_until_silence():
    """Record audio until silence detected."""
    print("\n🎤 Listening... (speak now)")

    audio_chunks = []
    silence_samples = 0
    speech_samples = 0
    silence_threshold_samples = int(SILENCE_DURATION * SAMPLE_RATE)
    min_speech_samples = int(MIN_SPEECH_DURATION * SAMPLE_RATE)

    def callback(indata, frames, time_info, status):
        nonlocal silence_samples, speech_samples
        volume = np.abs(indata).mean()

        if volume > SILENCE_THRESHOLD:
            speech_samples += frames
            silence_samples = 0
        else:
            silence_samples += frames

        audio_chunks.append(indata.copy())

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=callback):
        while True:
            time.sleep(0.1)
            if speech_samples > min_speech_samples and silence_samples > silence_threshold_samples:
                break
            if silence_samples > silence_threshold_samples * 3 and speech_samples == 0:
                return None

    if not audio_chunks:
        return None

    audio = np.concatenate(audio_chunks)
    return audio


def transcribe_deepgram(audio):
    """Transcribe audio using Deepgram REST API."""
    print("📝 Transcribing...")

    # Convert to WAV bytes
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes((audio * 32767).astype(np.int16).tobytes())

    audio_bytes = buf.getvalue()

    response = requests.post(
        "https://api.deepgram.com/v1/listen?model=nova-2&language=en-GB&smart_format=true",
        headers={
            "Authorization": f"Token {os.getenv('DEEPGRAM_API_KEY')}",
            "Content-Type": "audio/wav"
        },
        data=audio_bytes
    )

    result = response.json()
    transcript = result.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("transcript", "")
    return transcript


def capture_frame():
    """Capture a frame from the webcam."""
    print("📷 Capturing...")

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    for _ in range(5):
        cap.read()

    ret, frame = cap.read()
    cap.release()

    if not ret:
        return None

    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
    return base64.b64encode(buffer).decode('utf-8')


def analyze(text, image_b64):
    """Send to Claude Vision for analysis."""
    print("🧠 Thinking...")

    response = anthropic.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        system="""You are Airpiece, a hands-free AI assistant for fieldwork.
Keep responses concise (1-3 sentences) - they'll be spoken through an earpiece.
If asked to log something, confirm what you captured.
If asked a question about the scene, answer directly.""",
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_b64
                    }
                },
                {"type": "text", "text": text}
            ]
        }]
    )

    return response.content[0].text


def speak(text):
    """Speak text using macOS TTS."""
    print(f"🔊 {text}\n")
    subprocess.run(['say', '-r', '180', text], check=True)


def check_voice_command(text):
    """Check for voice control commands. Returns (command, should_process)."""
    text_lower = text.lower().strip()

    if "airpiece stop" in text_lower or "airpiece quit" in text_lower:
        return "stop", False
    elif "airpiece sleep" in text_lower or "airpiece pause" in text_lower:
        return "sleep", False
    elif "airpiece wake" in text_lower or "airpiece resume" in text_lower:
        return "wake", False
    elif "airpiece mute" in text_lower:
        return "mute", False
    elif "airpiece unmute" in text_lower:
        return "unmute", False

    return None, True


def main():
    print("=" * 50)
    print("AIRPIECE DEV PROTOTYPE")
    print("=" * 50)
    print("Speak naturally. I see what your webcam sees.")
    print("")
    print("Voice commands:")
    print("  'Airpiece sleep'  - pause listening")
    print("  'Airpiece wake'   - resume listening")
    print("  'Airpiece mute'   - turn off camera")
    print("  'Airpiece unmute' - turn on camera")
    print("  'Airpiece stop'   - quit")
    print("")
    print("Press Ctrl+C to exit.\n")

    # Check API keys
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Need ANTHROPIC_API_KEY")
        sys.exit(1)
    if not os.getenv("DEEPGRAM_API_KEY"):
        print("❌ Need DEEPGRAM_API_KEY")
        sys.exit(1)

    # Test camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot access webcam. Grant camera permission.")
        sys.exit(1)
    cap.release()

    print("✓ Camera ready")
    print("✓ API keys found\n")

    sleeping = False
    camera_muted = False

    while True:
        try:
            audio = record_until_silence()
            if audio is None:
                continue

            text = transcribe_deepgram(audio)
            if not text or len(text.strip()) < 2:
                continue

            print(f"You said: \"{text}\"")

            # Check for voice commands
            command, should_process = check_voice_command(text)

            if command == "stop":
                speak("Goodbye!")
                print("\n👋 Stopped by voice command")
                break
            elif command == "sleep":
                sleeping = True
                speak("Sleeping. Say Airpiece wake to resume.")
                print("😴 Sleeping...")
                continue
            elif command == "wake":
                sleeping = False
                speak("I'm back. How can I help?")
                print("👁️ Awake!")
                continue
            elif command == "mute":
                camera_muted = True
                speak("Camera muted. I can hear you but I'm not looking.")
                print("🙈 Camera muted")
                continue
            elif command == "unmute":
                camera_muted = False
                speak("Camera on. I can see again.")
                print("👁️ Camera on")
                continue

            # If sleeping, only respond to wake command
            if sleeping:
                continue

            # Capture and analyze
            if camera_muted:
                # No image, just respond to voice
                response = anthropic.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=300,
                    system="""You are Airpiece, a hands-free AI assistant for fieldwork.
Keep responses concise (1-3 sentences) - they'll be spoken through an earpiece.
The camera is currently muted so you cannot see anything.""",
                    messages=[{"role": "user", "content": text}]
                ).content[0].text
            else:
                image = capture_frame()
                if image is None:
                    speak("I couldn't capture from the camera.")
                    continue
                response = analyze(text, image)

            speak(response)

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            continue


if __name__ == "__main__":
    main()
