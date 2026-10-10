
import os
import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest


DATA_FILE = "data/telemetry.csv"

FEATURES = [
    "altitude",
    "speed",
    "battery",
    "gps_satellites"
]


def load_telemetry():
    df = pd.read_csv(DATA_FILE)

    for column in FEATURES:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    df = df.dropna(subset=FEATURES)
    return df.reset_index(drop=True)


def train_model(df):
    model = IsolationForest(
        n_estimators=100,
        contamination=0.02,
        random_state=42
    )

    model.fit(df[FEATURES])
    return model


# def detect_anomaly(model, telemetry):
#     """Classify one UAV telemetry reading."""

#     reading = pd.DataFrame([{
#         "altitude": telemetry["altitude"],
#         "speed": telemetry["speed"],
#         "battery": telemetry["battery"],
#         "gps_satellites": telemetry["gps_satellites"]
#     }])

#     prediction = model.predict(reading[FEATURES])[0]

#     return prediction == -1


def detect_anomaly(model, telemetry):
    """Classify one UAV telemetry reading."""

    battery = float(telemetry["battery"])

    # Rule-based critical battery alert
    if battery <= 10:
        return True

    # Existing ML anomaly detection
    reading = pd.DataFrame([{
        "altitude": telemetry["altitude"],
        "speed": telemetry["speed"],
        "battery": battery,
        "gps_satellites": telemetry["gps_satellites"]
    }])

    prediction = model.predict(reading[FEATURES])[0]

    return prediction == -1

def load_or_train_model():
    df = load_telemetry()

    if len(df) < 50:
        raise ValueError(
            "At least 50 valid telemetry records are required."
        )

    model_path = "ml/anomaly_model.joblib"

    if os.path.exists(model_path):
        model = joblib.load(model_path)
    else:
        model = train_model(df)
        joblib.dump(model, model_path)

    return model


if __name__ == "__main__":
    df = load_telemetry()

    if len(df) < 50:
        raise ValueError(
            "Collect at least 50 valid telemetry records "
            "before training."
        )

    model = load_or_train_model()


    # Test with deliberately unusual telemetry
    test_data = pd.DataFrame([
        {
            "altitude": 1000.0,
            "speed": 100.0,
            "battery": 1.0,
            "gps_satellites": 0
        }
    ])

    test_result = model.predict(test_data[FEATURES])

    print("\n--- Anomaly Detection Test ---")

    if test_result[0] == -1:
        print("Potential anomaly detected successfully!")
    else:
        print("Test reading classified as normal.")




    df["anomaly_prediction"] = model.predict(
        df[FEATURES]
    )

    df["anomaly_status"] = df[
        "anomaly_prediction"
    ].map({
        1: "Normal",
        -1: "Potential Anomaly"
    })

    anomalies = df[
        df["anomaly_prediction"] == -1
    ]

    print(f"Records analysed: {len(df)}")
    print(f"Potential anomalies: {len(anomalies)}")
    print("\nLatest telemetry classifications:")
    print(
        df[
            FEATURES + ["anomaly_status"]
        ].tail(10).to_string(index=False)
    )