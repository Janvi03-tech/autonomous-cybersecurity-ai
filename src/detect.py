def detect_suspicious(events, threshold=3):
    failed_count = {}

    for event in events:
        # Match failed login safely
        if event.get("event_type", "").lower() == "failed login":
            ip = event.get("source_ip")

            # Skip entries without a valid IP
            if not ip or ip == "No IP found":
                continue

            if ip not in failed_count:
                failed_count[ip] = 0

            failed_count[ip] += 1

    # Print counts and alert on suspicious IPs
    for ip, count in failed_count.items():
        print(f"{ip} → {count} failed logins")
        if count >= threshold:
            print(f" {ip} → Suspicious activity!")

    return failed_count