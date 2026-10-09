def normalize_event(event):
    if not isinstance(event, dict) or not event:
        return None

    normalized_event = {
        "timestamp": event.get("timestamp"),
        "event_type": event.get("event_type", "Unknown event"),
        "username": event.get("username"),
        "source_ip": event.get("source_ip"),
        "destination_ip": event.get("destination_ip"),
        "port": event.get("port"),
        "raw_message": event.get("raw_message", ""),
    }

    return normalized_event
