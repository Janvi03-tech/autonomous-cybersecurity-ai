import json
import pandas as pd

from feature import create_features


# Load normalized events
with open("data/normalized_logs.json", "r") as file:
    events = json.load(file)


# Create features
features = create_features(events)


# Convert features into a DataFrame
df = pd.DataFrame(features)


print(df)
X = df[
    [
        "failed_attempts",
        "successful_attempts",
        "total_attempts"
    ]
]
print(X)