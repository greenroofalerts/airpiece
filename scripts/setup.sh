#!/bin/bash
# Airpiece — Raspberry Pi 5 initial setup script
# Run this once after flashing Raspberry Pi OS (64-bit)

set -e

echo "=== Airpiece Setup ==="
echo ""

# System updates
echo "[1/7] Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Audio dependencies
echo "[2/7] Installing audio dependencies..."
sudo apt install -y \
    python3-pyaudio \
    portaudio19-dev \
    espeak \
    pulseaudio \
    pulseaudio-module-bluetooth \
    bluez \
    alsa-utils

# Camera dependencies
echo "[3/7] Installing camera dependencies..."
sudo apt install -y \
    python3-picamera2 \
    python3-libcamera \
    libcamera-apps

# GPS dependencies
echo "[4/7] Installing GPS tools..."
sudo apt install -y \
    gpsd \
    gpsd-clients

# Piper TTS
echo "[5/7] Installing Piper TTS..."
pip3 install piper-tts

# Download Piper voice model
echo "[5b/7] Downloading Piper voice model (en_GB-alba-medium)..."
mkdir -p ~/.local/share/piper/voices
cd ~/.local/share/piper/voices
if [ ! -f "en_GB-alba-medium.onnx" ]; then
    wget -q https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alba/medium/en_GB-alba-medium.onnx
    wget -q https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alba/medium/en_GB-alba-medium.onnx.json
fi
cd -

# Python dependencies
echo "[6/7] Installing Python dependencies..."
pip3 install -r requirements.txt

# Enable I2S and UART in boot config
echo "[7/7] Configuring boot overlays..."
BOOT_CONFIG="/boot/firmware/config.txt"

if ! grep -q "dtoverlay=i2s-mmap" "$BOOT_CONFIG" 2>/dev/null; then
    echo "" | sudo tee -a "$BOOT_CONFIG"
    echo "# Airpiece I2S microphone" | sudo tee -a "$BOOT_CONFIG"
    echo "dtoverlay=i2s-mmap" | sudo tee -a "$BOOT_CONFIG"
    echo "dtoverlay=googlevoicehat-soundcard" | sudo tee -a "$BOOT_CONFIG"
fi

if ! grep -q "enable_uart=1" "$BOOT_CONFIG" 2>/dev/null; then
    echo "" | sudo tee -a "$BOOT_CONFIG"
    echo "# Airpiece GPS UART" | sudo tee -a "$BOOT_CONFIG"
    echo "enable_uart=1" | sudo tee -a "$BOOT_CONFIG"
    echo "dtoverlay=disable-bt" | sudo tee -a "$BOOT_CONFIG"
fi

# Create .env template
if [ ! -f .env ]; then
    echo "ANTHROPIC_API_KEY=your_key_here" > .env
    echo "OPENAI_API_KEY=optional_for_whisper_api" >> .env
    echo "LOG_LEVEL=INFO" >> .env
    echo "Created .env — add your API keys before running."
fi

echo ""
echo "=== Setup complete ==="
echo "Next steps:"
echo "  1. Edit .env and add your ANTHROPIC_API_KEY"
echo "  2. Reboot: sudo reboot"
echo "  3. Wire up hardware (see docs/WIRING.md)"
echo "  4. Test hardware: python3 scripts/test_hardware.py"
echo "  5. Run: python3 firmware/main.py"
