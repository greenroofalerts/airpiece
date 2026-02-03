#!/usr/bin/env python3
"""Airpiece — Hardware connectivity test.

Run this after wiring everything up to verify each component works.
"""

import sys
import time


def test_camera():
    """Test Pi Camera Module 3."""
    print("\n[Camera] Testing...")
    try:
        from picamera2 import Picamera2
        cam = Picamera2()
        config = cam.create_still_configuration(main={"size": (640, 480)})
        cam.configure(config)
        cam.start()
        time.sleep(1)
        array = cam.capture_array()
        cam.stop()
        print(f"  OK — captured frame: {array.shape}")
        return True
    except ImportError:
        print("  SKIP — picamera2 not installed (not on a Pi?)")
        return False
    except Exception as e:
        print(f"  FAIL — {e}")
        return False


def test_microphone():
    """Test INMP441 I2S microphone."""
    print("\n[Microphone] Testing (recording 2 seconds)...")
    try:
        import pyaudio
        pa = pyaudio.PyAudio()
        stream = pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=480,
        )
        frames = []
        for _ in range(int(16000 / 480 * 2)):  # 2 seconds
            data = stream.read(480, exception_on_overflow=False)
            frames.append(data)
        stream.stop_stream()
        stream.close()
        pa.terminate()

        # Check if we got non-silent audio
        import struct
        samples = struct.unpack(f"<{len(b''.join(frames))//2}h", b"".join(frames))
        max_amp = max(abs(s) for s in samples)
        print(f"  OK — recorded {len(frames)} chunks, max amplitude: {max_amp}")
        if max_amp < 100:
            print("  WARNING — very low amplitude, mic may not be connected")
        return True
    except Exception as e:
        print(f"  FAIL — {e}")
        return False


def test_gps():
    """Test NEO-6M GPS module."""
    print("\n[GPS] Testing (waiting up to 5 seconds for data)...")
    try:
        import serial
        ser = serial.Serial("/dev/ttyAMA0", 9600, timeout=1)
        start = time.time()
        got_data = False
        while time.time() - start < 5:
            line = ser.readline().decode("ascii", errors="replace").strip()
            if line.startswith("$"):
                print(f"  OK — receiving NMEA data: {line[:60]}")
                got_data = True
                break
        ser.close()
        if not got_data:
            print("  FAIL — no NMEA data received (check TX/RX wiring)")
        return got_data
    except Exception as e:
        print(f"  FAIL — {e}")
        return False


def test_bluetooth():
    """Check if Bluetooth audio device is connected."""
    print("\n[Bluetooth] Checking for connected audio device...")
    try:
        import subprocess
        result = subprocess.run(
            ["pactl", "list", "sinks", "short"],
            capture_output=True, text=True, timeout=5,
        )
        if "bluez" in result.stdout:
            print(f"  OK — Bluetooth audio sink found")
            return True
        else:
            print("  FAIL — no Bluetooth audio device connected")
            print("  Hint: pair your earpiece with 'bluetoothctl'")
            return False
    except Exception as e:
        print(f"  FAIL — {e}")
        return False


def test_tts():
    """Test text-to-speech output."""
    print("\n[TTS] Testing speech output...")
    try:
        import subprocess
        result = subprocess.run(
            ["espeak", "-v", "en-gb", "Airpiece hardware test"],
            timeout=10,
        )
        if result.returncode == 0:
            print("  OK — did you hear 'Airpiece hardware test'?")
            return True
        else:
            print("  FAIL — espeak returned error")
            return False
    except Exception as e:
        print(f"  FAIL — {e}")
        return False


def main():
    print("=" * 40)
    print("  Airpiece Hardware Test")
    print("=" * 40)

    results = {
        "Camera": test_camera(),
        "Microphone": test_microphone(),
        "GPS": test_gps(),
        "Bluetooth": test_bluetooth(),
        "TTS": test_tts(),
    }

    print("\n" + "=" * 40)
    print("  Results")
    print("=" * 40)
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")

    failed = sum(1 for v in results.values() if not v)
    if failed == 0:
        print("\nAll tests passed. Ready to run: python3 firmware/main.py")
    else:
        print(f"\n{failed} test(s) failed. Check wiring and connections.")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
