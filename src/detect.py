import pandas as pd


# Load ML results
df = pd.read_csv("data/ml_results.csv")


# Convert prediction into readable words
df["status"] = df["prediction"].apply(
    lambda x: "anomaly" if x == -1 else "normal"
)


print("\nAnomaly Detection Results:")
print(df)


# Get only anomalies
anomalies = df[df["status"] == "anomaly"]


print("\nDetected Anomalies:")
print(anomalies)


# Save anomalies
anomalies.to_csv(
    "data/anomalies.csv",
    index=False
)


print("\nSaved anomalies to data/anomalies.csv")