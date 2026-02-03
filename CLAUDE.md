# Airpiece — Hands-Free AI Site Assistant

## What This Is
A hard-hat-mounted AI assistant for green roof site surveys. Camera always recording, voice-triggered interaction, bone conduction earpiece for responses. No screen, no hands.

## Use Cases
- Voice-tagged site observations: "log this — moss buildup on north parapet" → captures frame + transcript + GPS
- Species identification: "what plant is that?" → vision API identifies from camera frame
- Safety hazard detection: "any issues here?" → analyses scene for hazards
- End-of-day report generation from all captured data

## Hardware (RPi 5 Prototype)
- Raspberry Pi 5 (4GB) — main compute
- Pi Camera Module 3 (wide angle) — continuous capture
- INMP441 I2S MEMS microphone — voice input
- Bluetooth bone conduction earpiece — audio responses
- NEO-6M GPS module — geolocation
- 10Ah LiPo battery pack (USB-C PD) — all-day power
- 3D printed hard hat mount

## Architecture
```
[Mic] → [RPi5: VAD + wake word] → [Whisper API or local] → text
[Camera] → [RPi5: frame capture on trigger] → [Claude Vision API] → analysis
[GPS] → [RPi5: geotag all events]
[Response text] → [TTS: Piper local] → [Bluetooth earpiece]
All events → [SQLite log] → [Report generator]
```

## Tech Stack
- **Firmware/main loop**: Python 3.11+ on Raspberry Pi OS
- **Speech-to-text**: OpenAI Whisper (local small model or API)
- **Vision**: Claude Vision API (claude-sonnet-4-20250514 or later)
- **Text-to-speech**: Piper TTS (runs locally on Pi, no API needed)
- **Wake word**: Porcupine (local, low latency)
- **Database**: SQLite for event logging
- **Server**: Optional companion server for heavy processing / report viewing

## Project Structure
```
airpiece/
├── CLAUDE.md          # This file
├── firmware/          # Python code running on the RPi 5
│   ├── main.py        # Main event loop
│   ├── audio.py       # Mic capture, VAD, wake word detection
│   ├── camera.py      # Camera control, frame capture
│   ├── gps.py         # GPS module interface
│   ├── ai.py          # Claude Vision API + Whisper integration
│   ├── tts.py         # Piper TTS output to Bluetooth
│   ├── logger.py      # SQLite event logging
│   └── config.py      # Hardware pins, API keys, settings
├── server/            # Optional companion web server
│   ├── app.py         # Flask/FastAPI app for viewing logs/reports
│   └── report.py      # Report generation from logged events
├── scripts/           # Setup and utility scripts
│   ├── setup.sh       # RPi initial setup
│   └── test_hardware.py  # Hardware connectivity tests
├── docs/              # Documentation
│   ├── BOM.md         # Bill of materials with links
│   ├── WIRING.md      # Wiring diagram and pin connections
│   └── SETUP.md       # Full setup guide
├── tests/             # Unit tests
└── requirements.txt   # Python dependencies
```

## Key Decisions
- Local TTS (Piper) over cloud TTS — lower latency, works offline
- SQLite over Postgres — single device, no server needed
- Wake word detection — avoids always-streaming audio to cloud
- USB-C PD battery — standard drone/power bank batteries work
- Bone conduction — doesn't block ambient site sounds (safety critical)

## Commands
- `python firmware/main.py` — run the main assistant loop
- `python scripts/test_hardware.py` — verify all hardware connected
- `python server/app.py` — start companion web interface
