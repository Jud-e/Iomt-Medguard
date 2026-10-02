"""
Starter for training the Isolation Forest anomaly detector.

TODO (David):
1. Load CICIDS2017 / ECU IoMT dataset into `df` below (see ingestion/ once
   the dataset loader exists).
2. Pick the feature columns that represent traffic/payload characteristics
   (packet size, duration, protocol, request rate, etc).
3. Train, then save the model to ml/models/ so the stream consumer can load
   it for real-time scoring.
"""
import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

MODEL_OUT_PATH = "ml/models/isolation_forest.pkl"


def train(df: pd.DataFrame, feature_columns: list[str]):
    X = df[feature_columns]

    model = IsolationForest(
        n_estimators=100,
        contamination="auto",  # tune this once you see real anomaly rates
        random_state=42,
    )
    model.fit(X)

    joblib.dump(model, MODEL_OUT_PATH)
    print(f"Model saved to {MODEL_OUT_PATH}")
    return model


def score_to_risk(raw_score: float) -> int:
    """
    IsolationForest.decision_function() returns roughly [-0.5, 0.5],
    lower = more anomalous. Map that to a 0-100 risk score (100 = highest risk).
    TODO: calibrate this mapping against real data instead of a linear guess.
    """
    normalized = max(0.0, min(1.0, (0.5 - raw_score)))
    return round(normalized * 100)


if __name__ == "__main__":
    # Placeholder - replace with real dataset load
    print("Load your dataset into a DataFrame, then call train(df, feature_columns)")