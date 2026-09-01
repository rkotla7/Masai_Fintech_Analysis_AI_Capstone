"""
Part 1C -- Python payment reconciliation.

reconcile_payments(ledger_df, gateway_df) compares Paytm's ledger against the payment-gateway export 
and returns four DataFrames:
    1. missing_in_gateway  -- txns in ledger but absent from gateway export
    2. missing_in_ledger   -- txns in gateway export but absent from ledger
    3. amount_mismatches   -- txns present in both, amount_inr differs
    4. status_mismatches   -- txns present in both, status differs
"""

from pathlib import Path
import pandas as pd

def reconcile_payments(ledger_df, gateway_df):
    ledgers_ids = set(ledger_df["transaction_id"])
    gateway_ids = set(gateway_df["transaction_id"])

    # 1. Missing in gateway (present in ledger, absent from gateway export)

    missing_in_gateway_ids = ledgers_ids - gateway_ids
    missing_in_gateway = ledger_df[ledger_df["transaction_id"].isin(missing_in_gateway_ids)].copy()

    # 2. Missing in ledger (extra rows in gateway export not in our ledger)

    missing_in_ledger_ids = gateway_ids - ledgers_ids
    missing_in_ledger = gateway_df[gateway_df["transaction_id"].isin(missing_in_ledger_ids)].copy()

    # Common transaction_ids present in BOTH -> compare field-by-field

    common = pd.merge(ledger_df, gateway_df, on="transaction_id", suffixes=("_ledger", "_gateway")).copy()

    # 3. Amount mismatches (+ computed difference)
    amount_mismatches = common[common["amount_inr_ledger"] != common["amount_inr_gateway"]].copy()
    amount_mismatches["amount_diff"] = amount_mismatches["amount_inr_ledger"] - amount_mismatches["amount_inr_gateway"]
    amount_mismatches = amount_mismatches[["transaction_id", "amount_inr_ledger", "amount_inr_gateway", "amount_diff"]]

    # 4. Status mismatches
    status_mismatches = common[common["status_ledger"] != common["status_gateway"]].copy()

    return missing_in_gateway, missing_in_ledger, amount_mismatches, status_mismatches


if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent
    ledger = pd.read_csv(BASE_DIR /"ledger.csv", parse_dates=["transaction_time"])
    gateway = pd.read_csv(BASE_DIR / "gateway_export.csv", parse_dates=["transaction_time"])

    missing_in_gateway, missing_in_ledger, amount_mismatches, status_mismatches = reconcile_payments(ledger, gateway)

    print(f"Total transaction count in ledger:  {len(ledger)}")

    print(f"1. Transactions missing in gateway export: "
    f"{len(missing_in_gateway)} "
    f"({len(missing_in_gateway) / len(ledger) * 100:.2f}%) [Expected: 5%]")

    print(
        f"2. Transactions missing in ledger (extra in gateway): "
        f"{len(missing_in_ledger)} "
        f"({len(missing_in_ledger) / len(ledger) * 100:.2f}%) [Expected: 2%]")

    print(
        f"3. Amount mismatches: "
        f"{len(amount_mismatches)} "
        f"({len(amount_mismatches) / len(ledger) * 100:.2f}%) [Expected: 3%]")
    
    print(
        f"4. Status mismatches: "
        f"{len(status_mismatches)} "
        f"({len(status_mismatches) / len(ledger) * 100:.2f}%) [Expected: 2%]"
    )

        # Persist full outputs for the record
    missing_in_gateway.to_csv(BASE_DIR /"recon_missing_in_gateway.csv", index=False)
    missing_in_ledger.to_csv(BASE_DIR /"recon_missing_in_ledger.csv", index=False)
    amount_mismatches.to_csv(BASE_DIR /"recon_amount_mismatches.csv", index=False)
    status_mismatches.to_csv(BASE_DIR /"recon_status_mismatches.csv", index=False) 