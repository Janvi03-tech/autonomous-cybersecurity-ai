import pandas as pd
import json


# Load anomalies
df = pd.read_csv("data/anomalies.csv")


alerts = []


for index, row in df.iterrows():

    failed = int(row["failed_attempts"])

    # Decide severity
    if failed >= 5:
        severity = "HIGH"

    elif failed >= 3:
        severity = "MEDIUM"

    else:
        severity = "LOW"


    alert = {
        "alert_id": f"ALERT-{index + 1:03d}",
        "ip": row["ip"],
        "severity": severity,
        "reason": "Unusual login activity",
        "failed_attempts": failed,
        "successful_attempts": int(row["successful_attempts"]),
        "total_attempts": int(row["total_attempts"])
    }

    alerts.append(alert)


# Save alerts
with open("data/alerts.json", "w") as file:
    json.dump(alerts, file, indent=4)


print("\nGenerated Alerts:")

for alert in alerts:
    print(alert)

print("\nSaved alerts to data/alerts.json")