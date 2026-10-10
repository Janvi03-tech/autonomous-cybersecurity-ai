import os
from pathlib import Path

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=True)


def read_database_events(limit=1000):
    """Read recent PostgreSQL events as pipeline-friendly dictionaries."""
    if not 1 <= limit <= 10000:
        raise ValueError("limit must be between 1 and 10000")

    with psycopg.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        row_factory=dict_row,
    ) as connection:
        rows = connection.execute(
            """
            SELECT
                event_id,
                timestamp::text AS timestamp,
                event_type,
                username,
                host(source_ip) AS source_ip,
                host(destination_ip) AS destination_ip,
                port,
                raw_message,
                source
            FROM events
            ORDER BY timestamp DESC NULLS LAST, id DESC
            LIMIT %s
            """,
            (limit,),
        ).fetchall()

    events = [dict(row) for row in rows]
    events.reverse()
    return events
