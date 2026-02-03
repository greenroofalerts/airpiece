"""Airpiece companion server — view logs, reports, and captured images."""

import json
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "firmware"))
from logger import get_events, get_today_events
from config import CAPTURES_DIR, DATA_DIR

app = FastAPI(title="Airpiece")

# Serve captured images
if CAPTURES_DIR.exists():
    app.mount("/captures", StaticFiles(directory=str(CAPTURES_DIR)), name="captures")


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    events = get_today_events()
    rows = ""
    for e in events:
        img = ""
        if e.get("image_path"):
            fname = Path(e["image_path"]).name
            img = f'<img src="/captures/{fname}" style="max-width:200px;border-radius:4px">'
        gps = ""
        if e.get("latitude"):
            gps = f'{e["latitude"]:.5f}, {e["longitude"]:.5f}'
        rows += f"""
        <tr>
            <td style="white-space:nowrap">{e['timestamp'][:19]}</td>
            <td><span class="badge">{e['event_type']}</span></td>
            <td>{e.get('transcript', '') or ''}</td>
            <td>{e.get('ai_response', '') or ''}</td>
            <td>{img}</td>
            <td>{gps}</td>
        </tr>"""

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Airpiece Dashboard</title>
        <style>
            body {{ font-family: -apple-system, sans-serif; margin: 2rem; background: #0a0a0a; color: #e0e0e0; }}
            h1 {{ color: #4ade80; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ padding: 0.75rem; border-bottom: 1px solid #222; text-align: left; vertical-align: top; }}
            th {{ color: #888; font-weight: 500; text-transform: uppercase; font-size: 0.75rem; }}
            .badge {{ background: #1a3a2a; color: #4ade80; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; }}
            img {{ border: 1px solid #333; }}
            .count {{ color: #888; margin-bottom: 1rem; }}
        </style>
    </head>
    <body>
        <h1>Airpiece</h1>
        <p class="count">{len(events)} events today</p>
        <table>
            <thead>
                <tr><th>Time</th><th>Type</th><th>Transcript</th><th>AI Response</th><th>Image</th><th>GPS</th></tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
    </body>
    </html>
    """


@app.get("/api/events")
async def api_events(event_type: str = None, limit: int = 100):
    return get_events(event_type=event_type, limit=limit)


@app.get("/api/today")
async def api_today():
    return get_today_events()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
