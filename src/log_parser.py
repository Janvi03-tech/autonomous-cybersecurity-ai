from datetime import datetime


def parse_log(log):
    log = log.strip()

    if not log:
        return None

    parts = log.split()

    # Every supported log must begin with a valid timestamp.
    if len(parts) < 3:
        return None

    try:
        timestamp = datetime.strptime(
            f"{parts[0]} {parts[1]}",
            "%Y-%m-%d %H:%M:%S"
        )
    except ValueError:
        return None

    if "Failed login" in log:
        event_type = "Failed login"
    elif "Successful login" in log:
        event_type = "Successful login"
    elif "Process started:" in log:
        event_type = "Process started"
    elif "Network connection" in log:
        event_type = "Network connection"
    else:
        event_type = "Unknown event"

    username = None
    if "user" in parts:
        user_index = parts.index("user")
        if user_index + 1 < len(parts):
            username = parts[user_index + 1]

    source_ip = None
    destination_ip = None
    port = None

    if "from" in parts:
        ip_index = parts.index("from")
        if ip_index + 1 < len(parts):
            source_ip = parts[ip_index + 1]

    if event_type == "Network connection":
        if "to" in parts:
            ip_index = parts.index("to")
            if ip_index + 1 < len(parts):
                destination_ip = parts[ip_index + 1]

        if "port" in parts:
            port_index = parts.index("port")
            if port_index + 1 < len(parts):
                try:
                    port = int(parts[port_index + 1])
                except ValueError:
                    port = None

    return {
        "timestamp": timestamp.isoformat() + "Z",
        "event_type": event_type,
        "username": username,
        "source_ip": source_ip,
        "destination_ip": destination_ip,
        "port": port,
        "raw_message": log,
    }
