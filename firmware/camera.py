"""Camera control — continuous capture with on-demand frame grab."""

import base64
import io
import logging
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image
from config import CAMERA_RESOLUTION, JPEG_QUALITY, CAPTURES_DIR

log = logging.getLogger(__name__)

# picamera2 only available on Raspberry Pi — import conditionally
try:
    from picamera2 import Picamera2

    HAS_PICAMERA = True
except ImportError:
    HAS_PICAMERA = False
    log.warning("picamera2 not available — using mock camera")


class Camera:
    """Controls the Pi Camera Module 3."""

    def __init__(self):
        self.camera = None

    def start(self):
        """Initialize and start the camera."""
        if HAS_PICAMERA:
            self.camera = Picamera2()
            config = self.camera.create_still_configuration(
                main={"size": CAMERA_RESOLUTION}
            )
            self.camera.configure(config)
            self.camera.start()
            log.info("Camera started at %s", CAMERA_RESOLUTION)
        else:
            log.info("Mock camera started (no picamera2)")

    def stop(self):
        """Stop the camera."""
        if self.camera:
            self.camera.stop()
            log.info("Camera stopped")

    def capture_frame(self) -> Image.Image:
        """Capture a single frame and return as PIL Image."""
        if HAS_PICAMERA:
            array = self.camera.capture_array()
            return Image.fromarray(array)
        else:
            # Mock: return a small placeholder image for testing
            return Image.new("RGB", (320, 240), color=(100, 150, 100))

    def capture_and_save(self, label: str = "") -> Path:
        """Capture a frame, save to disk, return the file path."""
        frame = self.capture_frame()
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{label}.jpg" if label else f"{timestamp}.jpg"
        filepath = CAPTURES_DIR / filename
        frame.save(filepath, "JPEG", quality=JPEG_QUALITY)
        log.info("Frame saved: %s", filepath)
        return filepath

    def frame_to_base64(self, frame: Image.Image = None) -> str:
        """Capture (or convert) a frame to base64 JPEG for the vision API."""
        if frame is None:
            frame = self.capture_frame()
        buf = io.BytesIO()
        frame.save(buf, format="JPEG", quality=JPEG_QUALITY)
        return base64.standard_b64encode(buf.getvalue()).decode("utf-8")
