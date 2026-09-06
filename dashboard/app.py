import json
from pathlib import Path

import pandas as pd
import requests
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="Autonomous Cybersecurity AI",
    page_icon="🛡️",
    layout="wide"
)


# ============================================================
# PAGE TITLE
# ============================================================

st.title("🛡️ Autonomous Cybersecurity AI")

st.caption(
    "Prototype Security Operations Center (SOC) Dashboard"
)

st.divider()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_data(endpoint):
    """
    Get data from FastAPI backend.
    """

    try:
        response = requests.get(
            f"{API_URL}/{endpoint}",
            timeout=5
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException:
        st.error(
            "Could not connect to the FastAPI backend. "
            "Make sure the API is running."
        )

        return []


# ============================================================
# LOAD DATA
# ============================================================

alerts = get_data("alerts")

incidents = get_data("incidents")

correlations = get_data("correlations")


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "Dashboard",
        "Alerts",
        "Incidents",
        "MITRE Mapping",
        "Human Approval"
    ]
)


st.sidebar.divider()

st.sidebar.info(
    "Prototype Mode\n\n"
    "No real firewall or network changes are performed."
)


# ============================================================
# DASHBOARD PAGE
# ============================================================

if page == "Dashboard":

    st.header("Security Overview")

    # --------------------------------------------------------
    # Calculate statistics
    # --------------------------------------------------------

    total_alerts = len(alerts)

    total_incidents = len(incidents)

    high_severity = sum(
        1
        for incident in incidents
        if incident.get("severity") == "HIGH"
    )

    medium_severity = sum(
        1
        for incident in incidents
        if incident.get("severity") == "MEDIUM"
    )

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "🚨 Total Alerts",
            total_alerts
        )

    with col2:
        st.metric(
            "🔴 High Severity",
            high_severity
        )

    with col3:
        st.metric(
            "🟠 Medium Severity",
            medium_severity
        )

    with col4:
        st.metric(
            "⚠️ Incidents",
            total_incidents
        )

    st.divider()

    # --------------------------------------------------------
    # Incident Summary
    # --------------------------------------------------------

    st.subheader("Incident Summary")

    if incidents:

        incident_data = []

        for incident in incidents:

            incident_data.append({
                "Incident ID": incident.get("incident_id"),
                "IP Address": incident.get("ip"),
                "Severity": incident.get("severity"),
                "Type": incident.get("type"),
                "Failed Attempts": incident.get(
                    "failed_attempts"
                ),
                "Successful Attempts": incident.get(
                    "successful_attempts"
                )
            })

        incident_df = pd.DataFrame(
            incident_data
        )

        st.dataframe(
            incident_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.success(
            "No security incidents detected."
        )

    # --------------------------------------------------------
    # Suspicious IPs
    # --------------------------------------------------------

    st.subheader("Suspicious IP Addresses")

    if incidents:

        ip_data = []

        for incident in incidents:

            ip_data.append({
                "IP Address": incident.get("ip"),
                "Severity": incident.get("severity"),
                "Failed Attempts": incident.get(
                    "failed_attempts"
                )
            })

        ip_df = pd.DataFrame(ip_data)

        st.dataframe(
            ip_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No suspicious IP addresses.")


# ============================================================
# ALERTS PAGE
# ============================================================

elif page == "Alerts":

    st.header("🚨 Security Alerts")

    if not alerts:

        st.success(
            "No alerts available."
        )

    else:

        for alert in alerts:

            severity = alert.get(
                "severity",
                "UNKNOWN"
            )

            # Create expandable alert
            with st.expander(
                f"{alert.get('alert_id')} | "
                f"{severity} | "
                f"{alert.get('ip')}"
            ):

                col1, col2 = st.columns(2)

                with col1:

                    st.write(
                        f"**Alert ID:** "
                        f"{alert.get('alert_id')}"
                    )

                    st.write(
                        f"**IP Address:** "
                        f"{alert.get('ip')}"
                    )

                    st.write(
                        f"**Severity:** "
                        f"{severity}"
                    )

                    st.write(
                        f"**Reason:** "
                        f"{alert.get('reason')}"
                    )

                with col2:

                    st.write(
                        f"**Failed Attempts:** "
                        f"{alert.get('failed_attempts')}"
                    )

                    st.write(
                        f"**Successful Attempts:** "
                        f"{alert.get('successful_attempts')}"
                    )

                    st.write(
                        f"**Total Attempts:** "
                        f"{alert.get('total_attempts')}"
                    )


# ============================================================
# INCIDENTS PAGE
# ============================================================

elif page == "Incidents":

    st.header("🔥 Security Incidents")

    if not incidents:

        st.success(
            "No incidents detected."
        )

    else:

        for incident in incidents:

            st.subheader(
                f"{incident.get('incident_id')} — "
                f"{incident.get('type')}"
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.write(
                    f"**IP Address:** "
                    f"{incident.get('ip')}"
                )

            with col2:

                st.write(
                    f"**Severity:** "
                    f"{incident.get('severity')}"
                )

            with col3:

                st.write(
                    f"**Type:** "
                    f"{incident.get('type')}"
                )

            st.write(
                f"**Failed Attempts:** "
                f"{incident.get('failed_attempts')}"
            )

            st.write(
                f"**Successful Attempts:** "
                f"{incident.get('successful_attempts')}"
            )

            st.write(
                f"**Pattern:** "
                f"{incident.get('pattern')}"
            )

            if "mitre" in incident:

                st.write(
                    f"**MITRE ATT&CK:** "
                    f"{incident['mitre']['technique_id']} — "
                    f"{incident['mitre']['technique']}"
                )

                st.write(
                    f"**Tactic:** "
                    f"{incident['mitre']['tactic']}"
                )

            st.divider()


# ============================================================
# MITRE MAPPING PAGE
# ============================================================

elif page == "MITRE Mapping":

    st.header("🎯 MITRE ATT&CK Mapping")

    st.write(
        "Detected incidents mapped to MITRE ATT&CK techniques."
    )

    mitre_data = []

    for incident in incidents:

        if "mitre" in incident:

            mitre_data.append({
                "Incident": incident.get(
                    "incident_id"
                ),

                "IP Address": incident.get(
                    "ip"
                ),

                "Technique ID": incident["mitre"].get(
                    "technique_id"
                ),

                "Technique": incident["mitre"].get(
                    "technique"
                ),

                "Tactic": incident["mitre"].get(
                    "tactic"
                )
            })

    if mitre_data:

        mitre_df = pd.DataFrame(
            mitre_data
        )

        st.dataframe(
            mitre_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No MITRE mappings available."
        )


# ============================================================
# HUMAN APPROVAL PAGE
# ============================================================

elif page == "Human Approval":

    st.header("👤 Human Approval")

    st.warning(
        "Human approval is required before any response action."
    )

    st.write(
        "This prototype does NOT perform real network actions."
    )

    if not incidents:

        st.success(
            "There are no incidents requiring approval."
        )

    else:

        for incident in incidents:

            incident_id = incident.get(
                "incident_id"
            )

            ip = incident.get(
                "ip"
            )

            severity = incident.get(
                "severity"
            )

            st.subheader(
                f"{incident_id}"
            )

            st.write(
                f"**Target IP:** {ip}"
            )

            st.write(
                f"**Severity:** {severity}"
            )

            st.write(
                "**Proposed Action:** "
                "Simulate IP blocking"
            )

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    f"✅ Approve — {incident_id}",
                    key=f"approve_{incident_id}"
                ):

                    st.success(
                        f"Response approved for {ip}"
                    )

                    st.info(
                        "SIMULATION ONLY — "
                        "No real network change was performed."
                    )

            with col2:

                if st.button(
                    f"❌ Reject — {incident_id}",
                    key=f"reject_{incident_id}"
                ):

                    st.warning(
                        f"Response rejected for {ip}"
                    )

            st.divider()


# ============================================================
# FOOTER
# ============================================================

st.sidebar.divider()

st.sidebar.caption(
    "Autonomous Cybersecurity AI"
)

st.sidebar.caption(
    "Prototype Version"
)