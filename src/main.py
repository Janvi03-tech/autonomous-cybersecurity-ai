
import json
import os
from pathlib import Path

from dotenv import load_dotenv

from read_logs import read_logs
from log_parser import parse_log
from normalize import normalize_event
from feature import create_features
from db_reader import read_database_events


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=True)

# Set LOG_SOURCE=database to read PostgreSQL; default is sample.
LOG_SOURCE = os.getenv("LOG_SOURCE", "sample").strip().lower()


# STEP 1: Load events
if LOG_SOURCE == "database":
    events = read_database_events(limit=1000)
    print(f"Loaded {len(events)} events from PostgreSQL.")

elif LOG_SOURCE == "sample":
    logs = read_logs(str(BASE_DIR / "data" / "sample.log"))
    events = []

    for log in logs:
        if not log.strip():
            continue

        parsed_event = parse_log(log.strip())
        if parsed_event is None:
            continue

        normalized_event = normalize_event(parsed_event)
        if normalized_event is not None:
            events.append(normalized_event)

    print(f"Loaded {len(events)} events from the sample log.")

else:
    raise ValueError(
        f"Unsupported LOG_SOURCE={LOG_SOURCE!r}. "
        "Use 'sample' or 'database'."
    )


# STEP 2: Save normalized events
with open(BASE_DIR / "data" / "normalized_logs.json", "w", encoding="utf-8") as file:
    json.dump(events, file, indent=4, default=str)

print(f"Saved {len(events)} events to normalized_logs.json.")


# STEP 3: Create features
features = create_features(events)

print("\nML Features:\n")
print("IP\t\tFailed\tSuccessful\tTotal")

for feature in features:
    print(
        f"{feature['ip']}\t"
        f"{feature['failed_attempts']}\t"
        f"{feature['successful_attempts']}\t\t"
        f"{feature['total_attempts']}"
    )


# STEP 4: Save features
with open(BASE_DIR / "data" / "ml_features.json", "w", encoding="utf-8") as file:
    json.dump(features, file, indent=4)
