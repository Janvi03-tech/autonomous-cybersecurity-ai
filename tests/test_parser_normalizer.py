
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from log_parser import parse_log
from normalize import normalize_event


def test_parse_failed_login():
    log = "2026-10-10 09:30:00 Failed login for user alice from 192.168.1.50"

    event = parse_log(log)

    assert event is not None
    assert event["event_type"] == "Failed login"
    assert event["username"] == "alice"
    assert event["source_ip"] == "192.168.1.50"
    assert event["timestamp"] == "2026-10-10T09:30:00"


def test_parse_network_connection():
    log = "2026-10-10 09:31:00 Network connection from 192.168.1.50 to 10.0.0.25 port 443"

    event = parse_log(log)

    assert event is not None
    assert event["event_type"] == "Network connection"
    assert event["source_ip"] == "192.168.1.50"
    assert event["destination_ip"] == "10.0.0.25"
    assert event["port"] == 443


def test_parse_empty_log():
    assert parse_log("") is None


def test_parse_invalid_timestamp():
    log = "not-a-date 09:30:00 Failed login for user alice"

    assert parse_log(log) is None


def test_parse_invalid_network_port():
    log = "2026-10-10 09:31:00 Network connection from 192.168.1.50 to 10.0.0.25 port abc"

    assert parse_log(log) is None


def test_normalize_event_keeps_expected_fields():
    event = {
        "timestamp": "2026-10-10T09:30:00",
        "event_type": "Failed login",
        "username": "alice",
        "source_ip": "192.168.1.50",
        "destination_ip": None,
        "port": None,
        "raw_message": "example log",
        "extra_field": "should not be retained",
    }

    normalized = normalize_event(event)

    assert normalized["event_type"] == "Failed login"
    assert normalized["username"] == "alice"
    assert "extra_field" not in normalized
    assert set(normalized) == {
        "timestamp",
        "event_type",
        "username",
        "source_ip",
        "destination_ip",
        "port",
        "raw_message",
    }


def test_normalize_rejects_empty_or_invalid_input():
    assert normalize_event({}) is None
    assert normalize_event(None) is None
    assert normalize_event("not a dictionary") is None


def test_normalize_uses_defaults_for_missing_fields():
    normalized = normalize_event({"timestamp": "2026-10-10T09:30:00"})

    assert normalized["event_type"] == "Unknown event"
    assert normalized["raw_message"] == ""
    assert normalized["username"] is None
    assert normalized["source_ip"] is None

def test_parse_username_equals_format():
    log = (
        "2026-10-10 12:30:00 Failed login "
        "user=test_refresh from 192.168.1.99"
    )

    event = parse_log(log)

    assert event is not None
    assert event["username"] == "test_refresh"
    assert event["source_ip"] == "192.168.1.99"
