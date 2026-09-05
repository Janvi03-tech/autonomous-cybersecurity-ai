def create_features(events):

    ip_data = {}

    for event in events:

        ip = event["source_ip"]

        if ip not in ip_data:
            ip_data[ip] = {
                "failed_attempts": 0,
                "successful_attempts": 0
            }

        if event["event_type"] == "Failed login":
            ip_data[ip]["failed_attempts"] += 1

        elif event["event_type"] == "Successful login":
            ip_data[ip]["successful_attempts"] += 1

    features = []

    for ip, data in ip_data.items():

        failed = data["failed_attempts"]
        successful = data["successful_attempts"]

        total = failed + successful

        features.append({
            "ip": ip,
            "failed_attempts": failed,
            "successful_attempts": successful,
            "total_attempts": total
        })

    return features