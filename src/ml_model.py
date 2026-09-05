import json
import pandas as pd

from sklearn.ensemble import IsolationForest

from feature import create_features


# Load normalized events
with open("data/normalized_logs.json", "r") as file:
    events = json.load(file)


# Create features
features = create_features(events)


# Convert to DataFrame
df = pd.DataFrame(features)


# Select ML features
X = df[
    [
        "failed_attempts",
        "successful_attempts",
        "total_attempts"
    ]
]


# Create ML model
model = IsolationForest(
    contamination=0.25,
    random_state=42
)


# Train the model
model.fit(X)


# Predict anomalies
predictions = model.predict(X)


# Add prediction to our data
df["prediction"] = predictions


print(df)