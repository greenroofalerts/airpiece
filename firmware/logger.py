"""SQLite event logger — stores all observations, captures, and AI responses."""

import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path
from config import DB_PATH


def init_db():
    """Create the events table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            event_type TEXT NOT NULL,
            transcript TEXT,
            ai_response TEXT,
            image_path TEXT,
            latitude REAL,
            longitude REAL,
            metadata TEXT
        )
    """)
    conn.commit()
    conn.close()


def log_event(
    event_type: str,
    transcript: str = None,
    ai_response: str = None,
    image_path: str = None,
    latitude: float = None,
    longitude: float = None,
    metadata: dict = None,
) -> int:
    """Log an event and return its ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        """
        INSERT INTO events (timestamp, event_type, transcript, ai_response,
                           image_path, latitude, longitude, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now(timezone.utc).isoformat(),
            event_type,
            transcript,
            ai_response,
            image_path,
            latitude,
            longitude,
            json.dumps(metadata) if metadata else None,
        ),
    )
    conn.commit()
    event_id = cursor.lastrowid
    conn.close()
    return event_id


def get_events(event_type: str = None, limit: int = 100) -> list[dict]:
    """Retrieve recent events, optionally filtered by type."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    if event_type:
        rows = conn.execute(
            "SELECT * FROM events WHERE event_type = ? ORDER BY timestamp DESC LIMIT ?",
            (event_type, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM events ORDER BY timestamp DESC LIMIT ?", (limit,)
        ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_today_events() -> list[dict]:
    """Get all events from today (UTC)."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM events WHERE timestamp LIKE ? ORDER BY timestamp ASC",
        (f"{today}%",),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


# Initialize on import
init_db()
