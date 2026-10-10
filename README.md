# Autonomous Cybersecurity AI

A Python-based cybersecurity project for processing security logs, storing normalized events in PostgreSQL, exposing security data through a FastAPI backend, and supporting downstream anomaly detection and investigation.

## Features

- Security log parsing and normalization
- PostgreSQL-backed event storage
- Repeatable database schema initialization
- Sample-log import with duplicate handling
- FastAPI endpoints for event ingestion, filtering, and pagination
- Endpoints for alerts, incidents, correlations, and anomaly-related results
- Feature generation and anomaly detection with scikit-learn Isolation Forest
- Streamlit dashboard
- Local knowledge search for investigation support

## Prerequisites

- Python and pip
- PostgreSQL with the `psql` command-line client available
- Git (for cloning the repository)

Use a Python version supported by the dependencies listed in `requirements.txt`.

## Setup

From the project root, create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If `.venv` already exists, activate it rather than recreating it.

## Database Configuration

Create the PostgreSQL database `cybersecurity_ai` if it does not already exist. Configure the connection in a local `.env` file at the project root:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=cybersecurity_ai
DB_USER=postgres
DB_PASSWORD=your_local_password
```

Replace the password placeholder with your local PostgreSQL password. Do not commit `.env` or expose database credentials.

Ensure the PostgreSQL service is running.

### Initialize the database schema

Run this from the project root:

```powershell
python .\src\init_db.py
```

The initializer reads `sql/schema.sql` and runs it through `psql` using the database settings in `.env`. The schema uses `CREATE TABLE IF NOT EXISTS`, so it can be run again without replacing an existing `events` table.

The initializer creates the table for a fresh database. It does not migrate or repair an existing table with a different schema. The PostgreSQL database itself must exist before running the initializer.

## Import Sample Events

After initializing the database, import the sample logs:

```powershell
python .\src\import_sample_to_db.py
```

The importer uses deterministic event IDs and skips sample events that already exist. Re-running the import should not create duplicate sample records.

## Start the API

From the project root, run:

```powershell
python -m uvicorn src.api:app --reload
```

The local API is available at:

- Base URL: `http://127.0.0.1:8000`
- Interactive API documentation: `http://127.0.0.1:8000/docs`

### Main Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | API status and basic information |
| POST | `/logs` | Submit a log message for parsing and storage |
| GET | `/events` | Retrieve events with pagination and supported filters |
| GET | `/events/{event_id}` | Retrieve an event by ID |
| GET | `/alerts` | Retrieve alerts |
| GET | `/incidents` | Retrieve incident candidates |
| GET | `/correlations` | Retrieve event correlations |
| GET | `/anomalies` | Retrieve anomaly-related results |

Check `/docs` for the exact request schemas, parameters, and response formats.

The events endpoint supports pagination using `limit` and `offset`, plus filtering by `event_type` and `source_ip`.

## Normalized Event Schema

The parser and normalizer provide the following event fields:

| Field | Description |
|---|---|
| `timestamp` | Event timestamp in ISO 8601 format |
| `event_type` | Event category, such as `Failed login` or `Network connection` |
| `username` | Username when present |
| `source_ip` | Source IP address when present |
| `destination_ip` | Destination IP address when present |
| `port` | Network port when applicable |
| `raw_message` | Original log message |

Database records also have an event ID and source metadata. Consumers should use the API response schema as the authoritative contract for API fields.

## Run the Pipeline

```powershell
python .\src\main.py
```

The pipeline processes events according to the configured log source and generates its configured output files.

## Run Anomaly Detection

```powershell
python .\src\ml_model.py
```

Results are saved in `data/ml_results.csv`. Isolation Forest uses `-1` for flagged anomalies and `1` for samples classified as normal. These results are indicators for investigation, not proof of an attack.

## Start the Dashboard

In a separate terminal with the virtual environment activated:

```powershell
python -m streamlit run .\dashboard\app.py
```

## Run Tests

From the project root:

```powershell
python -m pytest -v
```

The test suite covers API behavior, request validation, log parsing, and normalization.

## Limitations and Security

- Sample logs are used for development and testing; production log-source integrations require separate configuration and validation.
- Anomaly predictions and correlations require investigation and should not be treated as proof of malicious activity.
- Keep credentials in environment variables and never commit `.env`.
- The database initializer requires PostgreSQL's `psql` client to be installed and available at the configured path or on `PATH`.
- Response actions should remain simulated until appropriate authorization, safeguards, and approval workflows are implemented.
- Run the API in a trusted development environment; review authentication, authorization, and deployment security before exposing it beyond localhost.
