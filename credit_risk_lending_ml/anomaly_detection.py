"""
Task 6: IsolationForest anomaly detection on txn_behaviour.csv, contamination matched
to the seeded anomaly proportion (15/265 approx 5.66%).

"""
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest


def run_anomaly_detection(csv_path="txn_behaviour.csv"):
    behaviour = pd.read_csv(csv_path)

    feature_cols = ["txn_hour", "is_new_device", "txn_amount_inr"]
    X = behaviour[feature_cols].copy()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    contamination_rate = 15 / 265
    iso = IsolationForest(random_state=42, contamination=contamination_rate)
    behaviour["anomaly_pred"] = iso.fit_predict(X_scaled)  # -1 = anomaly, 1 = normal
    behaviour["is_anomaly"] = (behaviour["anomaly_pred"] == -1).astype(int)

    seeded_anomalies = behaviour[behaviour["txn_id"].str.startswith("BTXNA")]
    flagged_seeded = seeded_anomalies[seeded_anomalies["is_anomaly"] == 1]
    recall = len(flagged_seeded) / len(seeded_anomalies)

    return {
        "behaviour": behaviour,
        "model": iso,
        "contamination_rate": contamination_rate,
        "n_seeded": len(seeded_anomalies),
        "n_flagged_seeded": len(flagged_seeded),
        "recall": recall,
    }


if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent
    result = run_anomaly_detection(BASE_DIR / "txn_behaviour.csv")

    print(f"Contamination rate used: {result['contamination_rate']:.4f}")
    print(f"Seeded anomalies: {result['n_seeded']}")
    print(f"Seeded anomalies flagged by IsolationForest: {result['n_flagged_seeded']}")
    print(f"Recall against seeded ground truth: {result['recall']:.2%}")

    result["behaviour"].to_csv(BASE_DIR / "txn_behaviour_scored.csv", index=False)
