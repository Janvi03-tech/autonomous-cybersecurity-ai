import json

with open("data/normalized_logs.json", "r") as file:
    events = json.load(file)

failed_logins = {}

for event in events:
    if event.get("event_type") == "Failed login":
        ip = event.get("source_ip", "No IP found")
        failed_logins[ip] = failed_logins.get(ip, 0) + 1

for ip, count in failed_logins.items():
    print(f"IP: {ip} | Failed attempts: {count}")