import json


# Load correlated events
with open("data/correlations.json", "r") as file:
    correlations = json.load(file)


incidents = []


for index, correlation in enumerate(correlations):

    failed = correlation["failed_attempts"]

    # Decide severity
    if failed >= 5:
        severity = "HIGH"

    elif failed >= 3:
        severity = "MEDIUM"

    else:
        severity = "LOW"

    incident = {
        "incident_id": f"INC-{index + 1:03d}",
        "ip": correlation["ip"],
        "severity": severity,
        "type": "Possible Brute Force",
        "pattern": correlation["pattern"],
        "failed_attempts": failed,
        "successful_attempts": correlation["successful_attempts"]
    }

    incidents.append(incident)


# Save incidents
with open("data/incidents.json", "w") as file:
    json.dump(incidents, file, indent=4)


print("\nCreated Incidents:")

for incident in incidents:
    print(incident)


print("\nSaved incidents to data/incidents.json")