import json


# Load normalized logs
with open("data/normalized_logs.json", "r") as file:
    events = json.load(file)


# Store login events by IP
ip_events = {}


for event in events:

    # Only process login events
    if event["event_type"] not in [
        "Failed login",
        "Successful login"
    ]:
        continue

    ip = event.get("source_ip")

    if not ip:
        continue

    # Create list for new IP
    if ip not in ip_events:
        ip_events[ip] = []

    ip_events[ip].append(event)


# Create correlation results
correlations = []


for ip, events in ip_events.items():

    failed = 0
    successful = 0

    for event in events:

        if event["event_type"] == "Failed login":
            failed += 1

        elif event["event_type"] == "Successful login":
            successful += 1

    # Look for suspicious pattern
    if failed >= 5 and successful >= 1:

        correlation = {
            "ip": ip,
            "failed_attempts": failed,
            "successful_attempts": successful,
            "pattern": "Multiple failed logins followed by successful login"
        }

        correlations.append(correlation)


# Save correlation results
with open("data/correlations.json", "w") as file:
    json.dump(correlations, file, indent=4)


print("\nCorrelated suspicious events:")

for correlation in correlations:
    print(correlation)


print("\nSaved correlations to data/correlations.json")