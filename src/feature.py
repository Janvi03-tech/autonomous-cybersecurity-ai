def create_features(events):

    ip_data = {}

    for event in events:

        # We only care about login events
        if event["event_type"] not in ["Failed login", "Successful login"]:
            continue

        ip = event.get("source_ip")

        if not ip:
            continue

        # Create an entry for a new IP
        if ip not in ip_data:
            ip_data[ip] = {
                "failed_attempts": 0,
                "successful_attempts": 0
            }

        # Count failed login
        if event["event_type"] == "Failed login":
            ip_data[ip]["failed_attempts"] += 1

        # Count successful login
        elif event["event_type"] == "Successful login":
            ip_data[ip]["successful_attempts"] += 1

    # Convert dictionary into a list
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