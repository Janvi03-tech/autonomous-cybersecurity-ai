import json

from read_logs import read_logs
from log_parser import parse_log
from normalize import normalize_event
from feature import create_features


# STEP 1: Read raw logs
logs = read_logs("data/sample.log")


# STEP 2: Parse and normalize logs
events = []

for log in logs:

    if log.strip() == "":
        continue

    parsed_event = parse_log(log.strip())

    normalized_event = normalize_event(parsed_event)

    events.append(normalized_event)


# STEP 3: Save normalized events to JSON

with open("data/normalized_logs.json", "w") as file:
    json.dump(events, file, indent=4)


print(f"Saved {len(events)} normalized events.")


# STEP 4: Create features

features = create_features(events)


# STEP 5: Display features

print("\nML Features:\n")

print("IP\t\t\tFailed\tSuccessful\tTotal")

for feature in features:

    print(
        f"{feature['ip']}\t"
        f"{feature['failed_attempts']}\t"
        f"{feature['successful_attempts']}\t\t"
        f"{feature['total_attempts']}"
    )


with open("data/ml_features.json", "w") as file:
    json.dump(features, file, indent=4)