import csv
import json

import os
from pathlib import Path
from uuid import uuid4
from datetime import datetime

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Autonomous Cybersecurity AI")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

load_dotenv(BASE_DIR / ".env")


class LogInput(BaseModel):
    message: str = Field(min_length=1, max_length=5000)


def get_connection():
    """Open a PostgreSQL connection using environment settings."""
    required = [
        "DB_HOST", "DB_PORT", "DB_NAME",
        "DB_USER", "DB_PASSWORD"
    ]
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise RuntimeError(
            "Missing database configuration: " + ", ".join(missing)
        )

    return psycopg.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        row_factory=dict_row,
    )


def parse_message(message):
    message = message.strip()

    if not message:
        return None

    parts = message.split()
    if len(parts) < 3:
        return None

    try:
        timestamp = datetime.strptime(
            f"{parts[0]} {parts[1]}",
            "%Y-%m-%d %H:%M:%S",
        )
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
    for index, part in enumerate(parts):
        if part == "user" and index + 1 < len(parts):
            username = parts[index + 1]
            break
        if part.startswith("user="):
            username = part.split("=", 1)[1] or None
            break

    source_ip = None
    if "from" in parts:
        index = parts.index("from")
        if index + 1 < len(parts):
            source_ip = parts[index + 1]

    destination_ip = None
    port = None

    if event_type == "Network connection":
        if "to" in parts:
            index = parts.index("to")
            if index + 1 < len(parts):
                destination_ip = parts[index + 1]

        if "port" in parts:
            index = parts.index("port")
            if index + 1 < len(parts):
                try:
                    port = int(parts[index + 1])
                except ValueError:
                    return None

    return {
        "event_id": str(uuid4()),
        "timestamp": timestamp,
        "event_type": event_type,
        "username": username,
        "source_ip": source_ip,
        "destination_ip": destination_ip,
        "port": port,
        "raw_message": message,
        "source": "api",
    }


@app.get("/")
def home():
    return {"message": "Autonomous Cybersecurity AI is running"}


@app.get("/alerts")
def get_alerts():
    try:
        with (DATA_DIR / "alerts.json").open(
            "r", encoding="utf-8"
        ) as file:
            return __import__("json").load(file)
    except (OSError, ValueError) as exc:
        raise HTTPException(
            status_code=500, detail="Could not read alerts."
        ) from exc


@app.get("/incidents")
def get_incidents():
    try:
        with (DATA_DIR / "incidents.json").open(
            "r", encoding="utf-8"
        ) as file:
            return __import__("json").load(file)
    except (OSError, ValueError) as exc:
        raise HTTPException(
            status_code=500, detail="Could not read incidents."
        ) from exc


@app.get("/correlations")
def get_correlations():
    try:
        with (DATA_DIR / "correlations.json").open(
            "r", encoding="utf-8"
        ) as file:
            return __import__("json").load(file)
    except (OSError, ValueError) as exc:
        raise HTTPException(
            status_code=500, detail="Could not read correlations."
        ) from exc


@app.post("/logs", status_code=201)
def ingest_log(log: LogInput):
    event = parse_message(log.message)

    if event is None:
        raise HTTPException(
            status_code=422,
            detail=(
                "Unsupported log format. Expected a timestamp "
                "like YYYY-MM-DD HH:MM:SS."
            ),
        )

    # Save the event to PostgreSQL first.
    try:
        with get_connection() as conn:
            saved = conn.execute(
                """
                INSERT INTO events (
                    event_id, timestamp, event_type, username,
                    source_ip, destination_ip, port, raw_message, source
                )
                VALUES (
                    %(event_id)s, %(timestamp)s, %(event_type)s,
                    %(username)s, %(source_ip)s, %(destination_ip)s,
                    %(port)s, %(raw_message)s, %(source)s
                )
                RETURNING *
                """,
                event,
            ).fetchone()

    except psycopg.Error as exc:
        print(f"PostgreSQL error while saving event: {exc}")
        database_error()

    return dict(saved)


@app.get("/events")
def get_events(
    limit: int = 100,
    offset: int = 0,
    event_type: str | None = None,
    source_ip: str | None = None,
):
    if limit < 1 or limit > 1000:
        raise HTTPException(
            status_code=422,
            detail="limit must be between 1 and 1000.",
        )

    if offset < 0:
        raise HTTPException(
            status_code=422,
            detail="offset must be zero or greater.",
        )

    query = "SELECT * FROM events"
    conditions = []
    params = []

    if event_type:
        conditions.append("event_type = %s")
        params.append(event_type)

    if source_ip:
        conditions.append("source_ip = %s::inet")
        params.append(source_ip)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY id DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    try:
        with get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
        return rows

    except psycopg.Error as exc:
        print(f"PostgreSQL error while reading events: {exc}")
        database_error()




@app.get("/events/{event_id}")
def get_event(event_id: str):
    try:
        with get_connection() as conn:
            event = conn.execute(
                "SELECT * FROM events WHERE event_id = %s",
                (event_id,),
            ).fetchone()
        if event is None:
            raise HTTPException(
                status_code=404, detail="Event not found."
            )
        return event
    except psycopg.Error as exc:
        print(f"PostgreSQL error while reading event: {exc}")
        database_error()

@app.get("/anomalies")
def get_anomalies():
    results_file = DATA_DIR / "ml_results.csv"

    try:
        with results_file.open("r", encoding="utf-8", newline="") as file:
            rows = list(csv.DictReader(file))

        anomalies = []
        for row in rows:
            try:
                prediction = int(row["prediction"])
                failed = int(row["failed_attempts"])
                successful = int(row["successful_attempts"])
                total = int(row["total_attempts"])
            except (KeyError, ValueError) as exc:
                raise HTTPException(
                    status_code=500,
                    detail="ML results file has an invalid format.",
                ) from exc

            if prediction == -1:
                anomalies.append({
                    "ip": row["ip"],
                    "failed_attempts": failed,
                    "successful_attempts": successful,
                    "total_attempts": total,
                    "prediction": prediction,
                    "status": "anomaly",
                    "note": "Model flag for investigation; not a confirmed attack.",
                })

        return {
            "count": len(anomalies),
            "anomalies": anomalies,
        }

    except OSError as exc:
        raise HTTPException(
            status_code=500,
            detail="Could not read ML results. Run the ML model first.",
        ) from exc
