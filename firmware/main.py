#!/usr/bin/env python3
"""Airpiece — main event loop.

Listens for wake word, captures speech, grabs a camera frame,
sends both to AI, and speaks the response through the earpiece.
"""

import logging
import signal
import sys
import time

from audio import AudioCapture
from camera import Camera
from gps import GPS
from ai import analyse_scene, transcribe_audio, generate_report
from tts import speak, speak_confirmation
from logger import log_event, get_today_events
from config import LOG_LEVEL

# --- Logging setup ---
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
log = logging.getLogger("airpiece")


class Airpiece:
    """Main application controller."""

    def __init__(self):
        self.audio = AudioCapture()
        self.camera = Camera()
        self.gps = GPS()
        self.running = False

    def start(self):
        """Initialize all hardware and start the main loop."""
        log.info("Starting Airpiece...")
        self.audio.start()
        self.camera.start()
        self.gps.start()
        self.running = True
        speak("Airpiece ready.")
        log.info("All systems ready.")

    def stop(self):
        """Clean shutdown."""
        log.info("Shutting down...")
        self.running = False
        self.audio.stop()
        self.camera.stop()
        self.gps.stop()
        speak("Airpiece shutting down.")
        log.info("Shutdown complete.")

    def run(self):
        """Main event loop."""
        self.start()

        try:
            while self.running:
                # Update GPS in background
                self.gps.update()

                # Listen for speech
                wav_bytes = self.audio.listen_for_speech()
                if wav_bytes is None:
                    continue

                # Transcribe speech
                log.info("Transcribing speech...")
                transcript = transcribe_audio(wav_bytes)
                if not transcript:
                    log.debug("Empty transcription, ignoring")
                    continue

                log.info("Heard: '%s'", transcript)

                # Handle special commands
                if self._handle_command(transcript):
                    continue

                # Capture camera frame
                frame_b64 = self.camera.frame_to_base64()
                image_path = self.camera.capture_and_save(
                    label=transcript[:30].replace(" ", "_")
                )

                # Get GPS position
                lat, lon = self.gps.get_position()
                context = f"GPS: {lat}, {lon}" if lat else "GPS: no fix"

                # Send to Claude Vision
                log.info("Sending to AI...")
                response = analyse_scene(frame_b64, transcript, context)
                log.info("AI response: %s", response)

                # Log the event
                log_event(
                    event_type="observation",
                    transcript=transcript,
                    ai_response=response,
                    image_path=str(image_path),
                    latitude=lat,
                    longitude=lon,
                )

                # Speak the response
                speak(response)

        except KeyboardInterrupt:
            log.info("Interrupted by user")
        finally:
            self.stop()

    def _handle_command(self, transcript: str) -> bool:
        """Handle built-in voice commands. Returns True if handled."""
        lower = transcript.lower().strip()

        if "generate report" in lower or "summarise today" in lower or "summary" in lower:
            speak("Generating report...")
            events = get_today_events()
            if not events:
                speak("No events logged today.")
                return True
            report = generate_report(events)
            log_event(event_type="report", ai_response=report)
            # Speak just the summary (first paragraph)
            summary = report.split("\n\n")[0]
            speak(summary)
            speak("Full report has been saved.")
            return True

        if "shut down" in lower or "stop listening" in lower:
            speak("Shutting down.")
            self.running = False
            return True

        if "status" in lower:
            lat, lon = self.gps.get_position()
            events = get_today_events()
            gps_status = f"GPS fix at {lat:.4f}, {lon:.4f}" if lat else "No GPS fix"
            speak(f"Airpiece active. {len(events)} events logged today. {gps_status}.")
            return True

        return False


def main():
    app = Airpiece()

    # Graceful shutdown on SIGTERM
    signal.signal(signal.SIGTERM, lambda *_: app.stop())

    app.run()


if __name__ == "__main__":
    main()
