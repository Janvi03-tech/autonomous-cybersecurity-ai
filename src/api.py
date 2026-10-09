import json
from pathlib import Path
from threading import Lock
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Autonomous Cybersecurity AI")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
EVENTS_FILE = DATA_DIR / "events.json"
EVENTS_LOCK = Lock()


class LogInput(BaseModel):
    message: str = Field(min_length=1, max_length=5000)


def load_events():
    if not EVENTS_FILE.exists():
        return []

    try:
        with EVENTS_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError) as exc:
        raise HTTPException(
            status_code=500,
            detail="Could not read stored events."
        ) from exc


def parse_message(message):
    from datetime import datetime

    parts = message.strip().split()
    if len(parts) < 2:
        return None

    try:
        timestamp = datetime.strptime(
            f"{parts[0]} {parts[1]}",
            "%Y-%m-%d %H:%M:%S"
        ).isoformat() + "Z"
    except ValueError:
        return None

    event_type = "Unknown event"
    if "Failed login" in message:
        event_type = "Failed login"
    elif "Successful login" in message:
        event_type = "Successful login"
    elif "Process started:" in message:
        event_type = "Process started"
    elif "Network connection" in message:
        event_type = "Network connection"

    username = None
    if "user" in parts:
        index = parts.index("user")
        if index + 1 < len(parts):
            username = parts[index + 1]

    source_ip = None
    if "from" in parts:
        index = parts.index("from")
        if index + 1 < len(parts):
            source_ip = parts[index + 1]
    elif "Network connection" in message and "from" in parts:
        index = parts.index("from")
        if index + 1 < len(parts):
            source_ip = parts[index + 1]

    return {
        "event_id": str(uuid4()),
        "timestamp": timestamp,
        "event_type": event_type,
        "username": username,
        "source_ip": source_ip,
        "raw_message": message.strip(),
        "source": "api"
    }


@app.get("/")
def home():
    return {"message": "Autonomous Cybersecurity AI is running"}


@app.get("/alerts")
def get_alerts():
    with (DATA_DIR / "alerts.json").open("r", encoding="utf-8") as file:
        return json.load(file)


@app.get("/incidents")
def get_incidents():
    with (DATA_DIR / "incidents.json").open("r", encoding="utf-8") as file:
        return json.load(file)


@app.get("/correlations")
def get_correlations():
    with (DATA_DIR / "correlations.json").open("r", encoding="utf-8") as file:
        return json.load(file)


@app.post("/logs", status_code=201)
def ingest_log(log: LogInput):
    event = parse_message(log.message)
    if event is None:
        raise HTTPException(
            status_code=422,
            detail="Unsupported log format. Expected a timestamp like YYYY-MM-DD HH:MM:SS."
        )

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with EVENTS_LOCK:
        events = load_events()
        events.append(event)
        with EVENTS_FILE.open("w", encoding="utf-8") as file:
            json.dump(events, file, indent=2)

    return event


@app.get("/events")
def get_events(limit: int = 100):
    if limit < 1 or limit > 1000:
        raise HTTPException(
            status_code=422,
            detail="limit must be between 1 and 1000."
        )

    return load_events()[-limit:]


@app.get("/events/{event_id}")
def get_event(event_id: str):
    for event in load_events():
        if event.get("event_id") == event_id:
            return event

    raise HTTPException(status_code=404, detail="Event not found.")
