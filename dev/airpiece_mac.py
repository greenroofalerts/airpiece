#!/usr/bin/env python3
"""
Airpiece Mac Dev Prototype
Voice → Webcam capture → Claude Vision → TTS response

Uses Google Cloud Speech-to-Text (same as Google Meet transcription)
"""

import os
import sys
import base64
import time
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


def transcribe_google(audio):
    """Transcribe audio using Google Cloud Speech-to-Text."""
    from google.cloud import speech
    import io
    import wave

    print("📝 Transcribing...")

    # Convert to WAV bytes
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes((audio * 32767).astype(np.int16).tobytes())

    client = speech.SpeechClient()
    audio_content = speech.RecognitionAudio(content=buf.getvalue())
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=SAMPLE_RATE,
        language_code="en-GB",
        enable_automatic_punctuation=True,
    )

    response = client.recognize(config=config, audio=audio_content)

    if response.results:
        return response.results[0].alternatives[0].transcript
    return ""


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
    import subprocess
    subprocess.run(['say', '-r', '180', text], check=True)


def main():
    print("=" * 50)
    print("AIRPIECE DEV PROTOTYPE")
    print("=" * 50)
    print("Using: Google Cloud STT + Claude Vision + macOS TTS")
    print("Speak naturally. I see what your webcam sees.")
    print("Press Ctrl+C to exit.\n")

    # Check Google Cloud credentials
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        print("⚠️  Set GOOGLE_APPLICATION_CREDENTIALS to your service account JSON")
        print("   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json")
        sys.exit(1)

    # Test camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot access webcam. Grant camera permission.")
        sys.exit(1)
    cap.release()

    while True:
        try:
            audio = record_until_silence()
            if audio is None:
                continue

            text = transcribe_google(audio)
            if not text or len(text.strip()) < 2:
                continue

            print(f"You said: \"{text}\"")

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
