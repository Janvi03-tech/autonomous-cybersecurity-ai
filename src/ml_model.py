import json
import pandas as pd
from sklearn.ensemble import IsolationForest

from feature import create_features


# Load normalized logs
with open("data/normalized_logs.json", "r") as file:
    events = json.load(file)


# Create features
features = create_features(events)


# Convert features into a DataFrame
df = pd.DataFrame(features)

print("\nFeatures:")
print(df)


# Select the numbers that ML will use
X = df[
    [
        "failed_attempts",
        "successful_attempts",
        "total_attempts"
    ]
]


# Create the ML model
model = IsolationForest(
    contamination=0.25,
    random_state=42
)


# Train the model
model.fit(X)


# Ask the model to find unusual data
predictions = model.predict(X)


# Add predictions to our table
df["prediction"] = predictions


# Save results
df.to_csv("data/ml_results.csv", index=False)


print("\nML Results:")
print(df)

print("\nSaved results to data/ml_results.csv")