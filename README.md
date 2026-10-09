# Autonomous Cybersecurity AI

A Python-based cybersecurity project for processing sample security logs, detecting potential anomalies, and displaying security information in a web dashboard.

## Features

* Log parsing and normalization
* Feature generation
* Anomaly detection with scikit-learn Isolation Forest
* FastAPI backend for alerts, incidents, and correlations
* Streamlit dashboard
* Local knowledge search for investigation support

## Setup

Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If `.venv` already exists, activate it instead of recreating it.

## Run the Pipeline

```powershell
python .\src\main.py
```

## Run Anomaly Detection

```powershell
python .\src\ml_model.py
```

Results are saved in `data/ml_results.csv`. Isolation Forest uses `-1` for flagged anomalies and `1` for samples classified as normal. These results are indicators for investigation, not proof of an attack.

## Start the API

```powershell
python -m uvicorn api:app --app-dir src --reload
```

API documentation: http://127.0.0.1:8000/docs

## Start the Dashboard

In a second terminal:

```powershell
python -m streamlit run .\dashboard\app.py
```

## Limitations

The current pipeline uses sample logs. The API reads existing project data files; PostgreSQL-backed storage has not yet been implemented. Anomaly predictions require investigation, and response actions should remain simulated during development.

## Security

Process only authorized logs. Never commit API keys, passwords, tokens, or `.env` files.
