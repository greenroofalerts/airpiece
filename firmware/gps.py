"""GPS module interface — reads position from NEO-6M via serial."""

import logging
import serial
import pynmea2
from config import GPS_SERIAL_PORT, GPS_BAUD_RATE

log = logging.getLogger(__name__)


class GPS:
    """Reads lat/lon from the NEO-6M GPS module over UART."""

    def __init__(self):
        self.serial_conn = None
        self.last_lat = None
        self.last_lon = None
        self.last_fix_time = None

    def start(self):
        """Open serial connection to GPS module."""
        try:
            self.serial_conn = serial.Serial(
                GPS_SERIAL_PORT, GPS_BAUD_RATE, timeout=1
            )
            log.info("GPS serial opened on %s", GPS_SERIAL_PORT)
        except serial.SerialException as e:
            log.warning("GPS not available: %s (continuing without GPS)", e)
            self.serial_conn = None

    def stop(self):
        """Close serial connection."""
        if self.serial_conn:
            self.serial_conn.close()
            log.info("GPS serial closed")

    def update(self) -> bool:
        """Read one NMEA sentence and update position. Returns True if fix updated."""
        if not self.serial_conn:
            return False

        try:
            line = self.serial_conn.readline().decode("ascii", errors="replace").strip()
            if line.startswith("$GPGGA") or line.startswith("$GPRMC"):
                msg = pynmea2.parse(line)
                if hasattr(msg, "latitude") and msg.latitude:
                    self.last_lat = msg.latitude
                    self.last_lon = msg.longitude
                    self.last_fix_time = getattr(msg, "timestamp", None)
                    return True
        except (pynmea2.ParseError, UnicodeDecodeError):
            pass
        return False

    def get_position(self) -> tuple[float | None, float | None]:
        """Return the most recent (lat, lon) or (None, None) if no fix."""
        return self.last_lat, self.last_lon

    def has_fix(self) -> bool:
        return self.last_lat is not None
