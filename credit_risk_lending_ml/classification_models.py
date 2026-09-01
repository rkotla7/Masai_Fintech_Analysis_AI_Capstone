"""
Task 3: Train Logistic Regression + Decision Tree on identical split.
Task 4: Full evaluation suite side by side, ROC/AUC.
Task 5: Generate risk-based pricing table.

"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (confusion_matrix, accuracy_score, precision_score, recall_score,
                              f1_score, roc_curve, roc_auc_score)
from eda_preprocessing import get_processed_data


def evaluate(model, X_test, y_test, name):
    pred = model.predict(X_test)
    proba = model.predict_proba(X_test)[:, 1]
    return {
        "model": name,
        "accuracy": accuracy_score(y_test, pred),
        "precision": precision_score(y_test, pred, zero_division=0),
        "recall": recall_score(y_test, pred, zero_division=0),
        "f1": f1_score(y_test, pred, zero_division=0),
        "auc": roc_auc_score(y_test, proba),
        "confusion_matrix": confusion_matrix(y_test, pred),
        "proba": proba,
    }


def build_risk_pricing_table(X_test, y_test, proba):
    pricing_df = X_test.copy()
    pricing_df["predicted_default_proba"] = proba
    pricing_df["actual_default"] = y_test.values

    pricing_df["risk_tier"] = pd.qcut(
        pricing_df["predicted_default_proba"], q=4,
        labels=["Tier 1 (Lowest Risk)", "Tier 2 (Low-Mid Risk)",
                "Tier 3 (Mid-High Risk)", "Tier 4 (Highest Risk)"]
    )

    rate_map = {
        "Tier 1 (Lowest Risk)": "9% - 11%",
        "Tier 2 (Low-Mid Risk)": "12% - 15%",
        "Tier 3 (Mid-High Risk)": "16% - 20%",
        "Tier 4 (Highest Risk)": "21% - 28%",
    }
    pricing_summary = pricing_df.groupby("risk_tier").agg(
        n_applicants=("actual_default", "count"),
        avg_predicted_proba=("predicted_default_proba", "mean"),
        observed_default_rate=("actual_default", "mean"),
    ).reset_index()
    pricing_summary["interest_rate_range"] = pricing_summary["risk_tier"].map(rate_map)
    pricing_summary = pricing_summary[["risk_tier", "n_applicants", "avg_predicted_proba",
                                        "observed_default_rate", "interest_rate_range"]]
    return pricing_summary


def save_roc_curves(res_lr, res_dt, y_test, path="roc_curves.png"):
    plt.figure(figsize=(6, 6))
    for r, color in zip([res_lr, res_dt], ["#1F4E78", "#C00000"]):
        fpr, tpr, _ = roc_curve(y_test, r["proba"])
        plt.plot(fpr, tpr, label=f"{r['model']} (AUC={r['auc']:.3f})", color=color)
    plt.plot([0, 1], [0, 1], "k--", alpha=0.4)
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curves - Logistic Regression vs Decision Tree")
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def save_confusion_matrices(res_lr, res_dt, path="confusion_matrices.png"):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, r in zip(axes, [res_lr, res_dt]):
        ax.imshow(r["confusion_matrix"], cmap="Blues")
        ax.set_title(r["model"])
        ax.set_xlabel("Predicted")
        ax.set_ylabel("Actual")
        ax.set_xticks([0, 1]); ax.set_xticklabels(["No Default", "Default"])
        ax.set_yticks([0, 1]); ax.set_yticklabels(["No Default", "Default"])
        for i in range(2):
            for j in range(2):
                ax.text(j, i, r["confusion_matrix"][i, j], ha="center", va="center",
                         color="white" if r["confusion_matrix"][i, j] > r["confusion_matrix"].max()/2 else "black")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def train_and_evaluate(csv_path="credit_applicants.csv"):
    data = get_processed_data(csv_path)
    X_train, X_test = data["X_train"], data["X_test"]
    y_train, y_test = data["y_train"], data["y_test"]

    logreg = LogisticRegression(max_iter=1000, random_state=42)
    logreg.fit(X_train, y_train)

    dtree = DecisionTreeClassifier(random_state=42)
    dtree.fit(X_train, y_train)

    res_lr = evaluate(logreg, X_test, y_test, "Logistic Regression")
    res_dt = evaluate(dtree, X_test, y_test, "Decision Tree")

    comparison = pd.DataFrame([
        {"Model": r["model"], "Accuracy": r["accuracy"], "Precision": r["precision"],
         "Recall": r["recall"], "F1": r["f1"], "AUC": r["auc"]}
        for r in [res_lr, res_dt]
    ])

    pricing_summary = build_risk_pricing_table(X_test, y_test, res_lr["proba"])
    is_monotonic = pricing_summary["observed_default_rate"].is_monotonic_increasing

    return {
        "logreg": logreg,
        "dtree": dtree,
        "res_lr": res_lr,
        "res_dt": res_dt,
        "comparison": comparison,
        "pricing_summary": pricing_summary,
        "is_monotonic": is_monotonic,
        "X_test": X_test,
        "y_test": y_test,
    }


if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent
    result = train_and_evaluate(BASE_DIR / "credit_applicants.csv")

    print(result["comparison"].to_string(index=False))
    result["comparison"].to_csv(BASE_DIR / "model_comparison.csv", index=False)

    save_roc_curves(result["res_lr"], result["res_dt"], result["y_test"], path=BASE_DIR / "roc_curves.png")
    save_confusion_matrices(result["res_lr"], result["res_dt"], path=BASE_DIR / "confusion_matrices.png")

    print("\nRisk-based pricing table:")
    print(result["pricing_summary"].to_string(index=False))
    result["pricing_summary"].to_csv(BASE_DIR / "risk_pricing_table.csv", index=False)

    print(f"\nMonotonicity check (observed default rate rises tier 1->4): {result['is_monotonic']}")
