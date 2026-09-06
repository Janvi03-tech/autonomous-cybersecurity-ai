import json


# Load incidents
with open("data/incidents.json", "r") as file:
    incidents = json.load(file)


for incident in incidents:

    if incident["type"] == "Possible Brute Force":

        incident["mitre"] = {
            "technique_id": "T1110",
            "technique": "Brute Force",
            "tactic": "Credential Access"
        }


# Save updated incidents
with open("data/incidents.json", "w") as file:
    json.dump(incidents, file, indent=4)


print("\nMITRE Mapping:")

for incident in incidents:

    print("\nIncident:", incident["incident_id"])
    print("IP:", incident["ip"])
    print("Technique:", incident["mitre"]["technique"])
    print("Technique ID:", incident["mitre"]["technique_id"])