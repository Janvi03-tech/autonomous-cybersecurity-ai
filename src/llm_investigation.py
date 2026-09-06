import json
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError

from rag import search_knowledge

# Load environment variables from .env file
load_dotenv()

# Create Gemini client (picks up GEMINI_API_KEY from environment)
client = genai.Client()

# Load incidents
with open("data/incidents.json", "r") as file:
    incidents = json.load(file)

# Process each incident
for incident in incidents:
    query = incident["type"]

    # Search knowledge base
    results = search_knowledge(query)

    knowledge = ""
    for result in results[:2]:
        knowledge += result["text"]
        knowledge += "\n\n"

    prompt = f"""
You are a cybersecurity analyst.

Analyze the following security incident.

Incident:
{json.dumps(incident, indent=2)}

Relevant security knowledge:
{knowledge}

Provide:

1. Investigation summary
2. Why the activity is suspicious
3. MITRE technique
4. Recommended investigation steps

Do not perform or recommend uncontrolled real-world actions.
"""

    response = None
    max_retries = 3

    # Handle temporary 503 high-demand spikes with retries
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
            )
            break
        except ServerError as e:
            if "503" in str(e) and attempt < max_retries - 1:
                wait_time = (attempt + 1) * 3
                print(f"[!] Server busy (503). Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise e

    print("\n==============================")
    print("INCIDENT:", incident["incident_id"])
    print("==============================")

    if response:
        print(response.text)

    # Rate limiting pause between loops
    time.sleep(1.5)