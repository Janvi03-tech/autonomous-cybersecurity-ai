
from datetime import datetime


def parse_log(log):
    log = log.strip()

    if not log:
        return None

    parts = log.split()
    if len(parts) < 3:
        return None

    try:
        timestamp = datetime.strptime(
            f"{parts[0]} {parts[1]}",
            "%Y-%m-%d %H:%M:%S",
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
    for index, part in enumerate(parts):
        if part == "user" and index + 1 < len(parts):
            username = parts[index + 1]
            break
        if part.startswith("user="):
            username = part.split("=", 1)[1] or None
            break

    source_ip = None
    if "from" in parts:
        ip_index = parts.index("from")
        if ip_index + 1 < len(parts):
            source_ip = parts[ip_index + 1]

    destination_ip = None
    if event_type == "Network connection" and "to" in parts:
        destination_index = parts.index("to")
        if destination_index + 1 < len(parts):
            destination_ip = parts[destination_index + 1]

    port = None
    if event_type == "Network connection" and "port" in parts:
        port_index = parts.index("port")
        if port_index + 1 < len(parts):
            try:
                port = int(parts[port_index + 1])
            except ValueError:
                return None

    return {
        "timestamp": timestamp.isoformat(),
        "event_type": event_type,
        "username": username,
        "source_ip": source_ip,
        "destination_ip": destination_ip,
        "port": port,
        "raw_message": log,
    }
