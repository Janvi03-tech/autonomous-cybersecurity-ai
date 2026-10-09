def create_features(events):
    ip_data = {}

    for event in events:
        # Safely skip empty or invalid events
        if not isinstance(event, dict):
            continue

        # Only count login events
        if event.get("event_type") not in [
            "Failed login",
            "Successful login"
        ]:
            continue

        ip = event.get("source_ip")
        if not ip:
            continue

        if ip not in ip_data:
            ip_data[ip] = {
                "failed_attempts": 0,
                "successful_attempts": 0
            }

        if event["event_type"] == "Failed login":
            ip_data[ip]["failed_attempts"] += 1
        else:
            ip_data[ip]["successful_attempts"] += 1

    features = []

    for ip, data in ip_data.items():
        total_attempts = (
            data["failed_attempts"]
            + data["successful_attempts"]
        )

        features.append({
            "ip": ip,
            "failed_attempts": data["failed_attempts"],
            "successful_attempts": data["successful_attempts"],
            "total_attempts": total_attempts
        })

    return features
