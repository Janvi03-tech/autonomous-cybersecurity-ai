import os
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

import psycopg
from dotenv import load_dotenv

from read_logs import read_logs
from log_parser import parse_log
from normalize import normalize_event


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=True)


def main():
    sample_file = BASE_DIR / "data" / "sample.log"
    logs = read_logs(str(sample_file))

    events = []
    for log in logs:
        if not log.strip():
            continue

        parsed = parse_log(log.strip())
        normalized = normalize_event(parsed)

        if normalized:
            events.append(normalized)

    inserted = 0
    skipped = 0

    with psycopg.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    ) as connection:
        for event in events:
            # A deterministic ID makes repeated imports idempotent.
            event_id = str(
                uuid5(
                    NAMESPACE_URL,
                    "autonomous-cybersecurity-ai:sample:"
                    + event["raw_message"],
                )
            )

            result = connection.execute(
                """
                INSERT INTO events (
                    event_id, timestamp, event_type, username,
                    source_ip, destination_ip, port, raw_message, source
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (event_id) DO NOTHING
                RETURNING id
                """,
                (
                    event_id,
                    event["timestamp"],
                    event["event_type"],
                    event["username"],
                    event["source_ip"],
                    event["destination_ip"],
                    event["port"],
                    event["raw_message"],
                    "sample",
                ),
            )

            if result.fetchone():
                inserted += 1
            else:
                skipped += 1

    print(f"Sample events parsed: {len(events)}")
    print(f"New events inserted: {inserted}")
    print(f"Duplicates skipped: {skipped}")


if __name__ == "__main__":
    main()
