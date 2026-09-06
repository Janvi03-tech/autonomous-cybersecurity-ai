import json

from fastapi import FastAPI


app = FastAPI(
    title="Autonomous Cybersecurity AI"
)


@app.get("/")
def home():

    return {
        "message": "Autonomous Cybersecurity AI is running"
    }


@app.get("/alerts")
def get_alerts():

    with open("data/alerts.json", "r") as file:
        alerts = json.load(file)

    return alerts


@app.get("/incidents")
def get_incidents():

    with open("data/incidents.json", "r") as file:
        incidents = json.load(file)

    return incidents


@app.get("/correlations")
def get_correlations():

    with open("data/correlations.json", "r") as file:
        correlations = json.load(file)

    return correlations