def normalize_event(event):

    normalized_event = {
        "timestamp": event["date"] + " " + event["time"],
        "event_type": event["event_type"],
        "source_ip": event["source_ip"] if "source_ip" in event else "No IP found"
    }

    return normalized_event