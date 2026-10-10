
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fastapi.testclient import TestClient
from api import app
client = TestClient(app)
from unittest.mock import MagicMock, patch

def test_home_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_events_reject_zero_limit():
    response = client.get("/events?limit=0")
    assert response.status_code == 422


def test_events_reject_negative_offset():
    response = client.get("/events?offset=-1")
    assert response.status_code == 422


def test_post_logs_rejects_invalid_timestamp():
    response = client.post(
        "/logs",
        json={"message": "this is not a valid timestamp"},
    )
    assert response.status_code == 422


def test_get_missing_event_returns_404():
    response = client.get("/events/does-not-exist-123")
    assert response.status_code == 404



@patch("api.get_connection")
def test_events_returns_results_with_pagination(mock_get_connection):
    mock_conn = MagicMock()
    mock_get_connection.return_value.__enter__.return_value = mock_conn
    mock_conn.execute.return_value.fetchall.return_value = [
        {
            "event_id": "test-event-1",
            "event_type": "Failed login",
        }
    ]

    response = client.get("/events?limit=10&offset=0")

    assert response.status_code == 200
    assert response.json() == [
        {
            "event_id": "test-event-1",
            "event_type": "Failed login",
        }
    ]
    mock_conn.execute.assert_called_once()


@patch("api.get_connection")
def test_events_filters_by_event_type(mock_get_connection):
    mock_conn = MagicMock()
    mock_get_connection.return_value.__enter__.return_value = mock_conn
    mock_conn.execute.return_value.fetchall.return_value = []

    response = client.get("/events?event_type=Failed%20login")

    assert response.status_code == 200
    assert response.json() == []

    sql, params = mock_conn.execute.call_args.args
    assert "event_type = %s" in sql
    assert "Failed login" in params


@patch("api.get_connection")
def test_events_filters_by_source_ip(mock_get_connection):
    mock_conn = MagicMock()
    mock_get_connection.return_value.__enter__.return_value = mock_conn
    mock_conn.execute.return_value.fetchall.return_value = []

    response = client.get("/events?source_ip=192.168.1.50")

    assert response.status_code == 200
    assert response.json() == []

    sql, params = mock_conn.execute.call_args.args
    assert "source_ip = %s::inet" in sql
    assert "192.168.1.50" in params

def test_post_logs_parses_username_equals_format():
    response = client.post(
        "/logs",
        json={
            "message": (
                "2026-10-10 12:31:00 Failed login "
                "user=test_refresh from 192.168.1.99"
            )
        },
    )

    # A database connection is needed for a successful insert.
    # This test should mock it so no real record is created.


def test_post_logs_parses_username_equals_format():
    saved_event = {
        "event_id": "test-user-parser-id",
        "timestamp": "2026-10-10T12:31:00",
        "event_type": "Failed login",
        "username": "test_refresh",
        "source_ip": "192.168.1.99",
        "destination_ip": None,
        "port": None,
        "raw_message": (
            "2026-10-10 12:31:00 Failed login "
            "user=test_refresh from 192.168.1.99"
        ),
        "source": "api",
    }

    mock_connection = MagicMock()
    mock_connection.execute.return_value.fetchone.return_value = saved_event

    mock_get_connection = MagicMock()
    mock_get_connection.return_value.__enter__.return_value = mock_connection

    with patch("api.get_connection", mock_get_connection):
        response = client.post(
            "/logs",
            json={
                "message": (
                    "2026-10-10 12:31:00 Failed login "
                    "user=test_refresh from 192.168.1.99"
                )
            },
        )

    assert response.status_code == 201
    assert response.json()["username"] == "test_refresh"

    # Verify the username passed to the database insert.
    sql, params = mock_connection.execute.call_args.args
    assert params["username"] == "test_refresh"
