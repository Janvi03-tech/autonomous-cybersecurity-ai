def parse_log(log):
    parts = log.split()

    date = parts[0]
    time = parts[1]

    if "Failed login" in log:
        event_type = "Failed login"
    elif "Successful login" in log:
        event_type = "Successful login"
    else:
        event_type = "Unkown event"

    # The IP address is the last element in the line
    source_ip = parts[-1]

    return {
        "date": date,
        "time": time,
        "event_type": event_type,
        "source_ip": source_ip       # <-- ADD THIS LINE
    }