"""
Task 1 (EDA) + Task 2 (thin-file flag generation,Stratified train/test split,Median imputation from TRAIN data, Encode employment_type, StandardScaler fit on TRAIN data ONLY).

use `from eda_preprocessing import get_processed_data` to call the data.
"""
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


def get_processed_data(csv_path="credit_applicants.csv"):
    df = pd.read_csv(csv_path)

    default_rate = df["default"].mean()
    missing_pct = df["credit_bureau_score"].isna().mean()

    # Engineer is_thin_file directly from raw (missing/not-missing) data -- safe pre-split.
    df["is_thin_file"] = df["credit_bureau_score"].isna().astype(int)

    feature_cols = ["age", "monthly_income_inr", "existing_loans_count", "credit_utilization_ratio",
                     "upi_monthly_inflow_inr", "bounced_payments_count", "credit_bureau_score",
                     "employment_type", "is_thin_file"]
    X = df[feature_cols].copy()
    y = df["default"].copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    # Median imputation -- computed from TRAIN ONLY, applied to both splits
    train_median = X_train["credit_bureau_score"].median()
    X_train["credit_bureau_score"] = X_train["credit_bureau_score"].fillna(train_median)
    X_test["credit_bureau_score"] = X_test["credit_bureau_score"].fillna(train_median)

    # Encode employment_type (one-hot)
    X_train = pd.get_dummies(X_train, columns=["employment_type"], drop_first=False)
    X_test = pd.get_dummies(X_test, columns=["employment_type"], drop_first=False)
    X_test = X_test.reindex(columns=X_train.columns, fill_value=0)

    # Scale numeric features, fit on TRAIN ONLY
    numeric_cols = ["age", "monthly_income_inr", "existing_loans_count", "credit_utilization_ratio",
                     "upi_monthly_inflow_inr", "bounced_payments_count", "credit_bureau_score"]
    scaler = StandardScaler()
    X_train[numeric_cols] = scaler.fit_transform(X_train[numeric_cols])
    X_test[numeric_cols] = scaler.transform(X_test[numeric_cols])

    return {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "train_median": train_median,
        "numeric_cols": numeric_cols,
        "default_rate": default_rate,
        "missing_pct": missing_pct,
        "scaler": scaler,
    }


if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent
    path = BASE_DIR / "credit_applicants.csv"
    data = get_processed_data(path)
    print(f"Default rate: {data['default_rate']:.4f}")
    print(f"Missing credit_bureau_score: {data['missing_pct']:.4f}")
    print(f"Train-derived median used for imputation: {data['train_median']:.2f}")
    print(f"X_train shape: {data['X_train'].shape}, X_test shape: {data['X_test'].shape}")