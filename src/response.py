import json


def simulate_response(incident):

    action = {
        "incident_id": incident["incident_id"],
        "action": "BLOCK_IP",
        "target": incident["ip"],
        "status": "SIMULATED",
        "message": "IP blocking was simulated. No real network changes were made."
    }

    return action


# Load incidents
with open("data/incidents.json", "r") as file:
    incidents = json.load(file)


print("\nSimulated Response\n")


for incident in incidents:

    action = simulate_response(incident)

    print(action)