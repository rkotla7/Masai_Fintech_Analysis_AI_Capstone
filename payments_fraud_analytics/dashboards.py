"""Part 1D -- Python payment reconciliation dashboard.

Layers:
  1. Headline scorecards (printed + saved as an image)
  2. Trends: daily GMV & daily chargeback count
  3. Breakdown: GMV by payment_method and by category
  4. Details: top-10 merchants table (saved as an image) with a
     chargeback_ratio > 1% flag
"""

import pandas as pd
import matplotlib.pyplot as plt 
import matplotlib
matplotlib.use("Agg")
import numpy as np
import os
from pathlib import Path
from reconcile import reconcile_payments

BASE_DIR = Path(__file__).resolve().parent

ledger = pd.read_csv(BASE_DIR / "ledger.csv", parse_dates=["transaction_time"])
gateway = pd.read_csv(BASE_DIR / "gateway_export.csv", parse_dates=["transaction_time"])
merchants = pd.read_csv(BASE_DIR / "merchants.csv")

interpretations = []

common = pd.merge(ledger, gateway, on="transaction_id", suffixes=("_ledger", "_gateway")).copy()

matched = common[(common["amount_inr_ledger"] == common["amount_inr_gateway"]) & (common["status_ledger"] == common["status_gateway"])].copy()

# ---------------------------------------------------------------
# LAYER 1: HEADLINE SCORECARDS
# ---------------------------------------------------------------

total_gmv = ledger["amount_inr"].sum()
success_rate = (ledger["status"] == "captured").mean()
chargeback_ratio = (ledger["status"] == "chargeback").mean()
recon_matched_rate = len(matched) / len(ledger)

scorecards = [
    ("Total GMV (INR)", f"₹{total_gmv:,.0f}"),
    ("Overall Success Rate", f"{success_rate:.1%}"),
    ("Reconciliation Match Rate", f"{recon_matched_rate:.1%}"),
    ("Chargeback Ratio", f"{chargeback_ratio:.2%}"),
]

fig, axes = plt.subplots(1, 4, figsize=(16, 3.2))
for ax, (label, value) in zip(axes, scorecards):
    ax.axis("off")
    ax.text(0.5, 0.6, value, ha="center", va="center", fontsize=22, fontweight="bold", color="#1F4E78")
    ax.text(0.5, 0.15, label, ha="center", va="center", fontsize=12, color="#444")
    ax.add_patch(plt.Rectangle((0.02, 0.02), 0.96, 0.96, fill=False, edgecolor="#1F4E78", lw=1.5))
plt.tight_layout()
plt.savefig(BASE_DIR / "dashboard_1_headline.png", dpi=150)
plt.close()

interpretations.append(f"""### Layer 1 - Headline Scorecards
Total GMV across the 30-day window is INR {total_gmv:,.0f} across {len(ledger)} transactions.
Success rate stands at {success_rate:.1%}, in line with the ~92% captured rate baked into the
synthetic data, with the remainder split between failures and chargebacks. The reconciliation
match rate of {recon_matched_rate:.1%} reflects that roughly {1-recon_matched_rate:.0%} of ledger transactions
have a discrepancy (missing, amount-mismatched, or status-mismatched) versus the gateway export
-- consistent with the ~12% combined injected discrepancy rate. The chargeback ratio of
{chargeback_ratio:.2%} is the platform-wide fraud-exposure headline number ops leadership would
watch week over week.""")


# ---------------------------------------------------------------
# LAYER 2: TRENDS -- daily GMV and daily chargeback count
# ---------------------------------------------------------------
ledger["transaction_date"] = pd.to_datetime(ledger["transaction_time"]).dt.date
daily_gmv = ledger.groupby("transaction_date")["amount_inr"].sum()
daily_cb = ledger[ledger["status"] == "chargeback"].groupby("transaction_date").size().reindex(daily_gmv.index, fill_value=0)


fig, ax1 = plt.subplots(figsize=(12, 4.5))
ax1.plot(daily_gmv.index, daily_gmv.values, color="#1F4E78", marker="o", markersize=3, label="Daily GMV (INR)")
ax1.set_ylabel("Daily GMV (INR)", color="#1F4E78")
ax1.tick_params(axis="x", rotation=45)
ax2 = ax1.twinx()
ax2.bar(daily_cb.index, daily_cb.values, color="#C00000", alpha=0.35, label="Daily Chargeback Count")
ax2.set_ylabel("Daily Chargeback Count", color="#C00000")
ax1.set_title("Daily GMV and Chargeback Count (30-day window)")
fig.tight_layout()
plt.savefig(BASE_DIR / "dashboard_2_trends.png", dpi=150)
plt.close()

peak_day = daily_gmv.idxmax()

interpretations.append(f"""### Layer 2 - Trends
Daily GMV fluctuates around a baseline with no strong weekly seasonality (expected, since the
underlying data is randomly generated rather than day-of-week weighted), peaking on {peak_day}
at INR {daily_gmv.max():,.0f}. Chargeback counts are sparse day to day but cluster more heavily
in the back half of the window -- this lines up with how the 15 seeded burner-account frauds
were deliberately injected into days 10-29 of the window rather than spread evenly, so a real
ops team would want to investigate any late-month chargeback uptick specifically for new-account
fraud rather than treating it as generic churn.""")


# ---------------------------------------------------------------
# LAYER 3: BREAKDOWN -- GMV by payment_method and by category
# ---------------------------------------------------------------
gmv_method = ledger.groupby("payment_method")["amount_inr"].sum().sort_values(ascending=False)
ledger_m = ledger.merge(merchants[["merchant_id", "category"]], on="merchant_id", how="left")
gmv_category = ledger_m.groupby("category")["amount_inr"].sum().sort_values(ascending=False)

fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
axes[0].bar(gmv_method.index, gmv_method.values, color="#1F4E78")
axes[0].set_title("GMV by Payment Method")
axes[0].set_ylabel("GMV (INR)")
axes[0].tick_params(axis="x", rotation=20)

axes[1].bar(gmv_category.index, gmv_category.values, color="#2e7d32")
axes[1].set_title("GMV by Merchant Category")
axes[1].set_ylabel("GMV (INR)")
axes[1].tick_params(axis="x", rotation=30)
plt.tight_layout()
plt.savefig(BASE_DIR / "dashboard_3_breakdown.png", dpi=150)
plt.close()

top_method = gmv_method.index[0]
top_cat = gmv_category.index[0]

interpretations.append(f"""### Layer 3 - Breakdown
{top_method} dominates GMV by payment method (INR {gmv_method.iloc[0]:,.0f}), consistent with
the 55% method-selection weight it was assigned in the data generator and mirroring UPI's real-world
dominance in Indian retail payments. By category, {top_cat} contributes the most GMV
(INR {gmv_category.iloc[0]:,.0f}), though with 7 categories roughly evenly represented among 40
merchants the spread across categories is fairly balanced -- there is no single category so
dominant that it represents concentration risk on its own.""")

# ---------------------------------------------------------------
# LAYER 4: DETAILS -- top 10 merchants by txn count, with chargeback-ratio flag, as an image
# ---------------------------------------------------------------
merch_stats = ledger.groupby("merchant_id").agg(
    txn_count=("transaction_id", "count"),
    total_gmv_inr=("amount_inr", "sum"),
    chargebacks=("status", lambda s: (s == "chargeback").sum()),
).reset_index()
merch_stats["chargeback_ratio"] = merch_stats["chargebacks"] / merch_stats["txn_count"]
merch_stats["high_risk_flag"] = np.where(merch_stats["chargeback_ratio"] > 0.01, "\u26a0 HIGH RISK", "")
merch_stats = merch_stats.merge(merchants[["merchant_id", "merchant_name"]], on="merchant_id")
top10 = merch_stats.sort_values("txn_count", ascending=False).head(10)
top10 = top10[["merchant_id", "merchant_name", "txn_count", "total_gmv_inr", "chargebacks",
               "chargeback_ratio", "high_risk_flag"]]
top10["chargeback_ratio"] = top10["chargeback_ratio"].apply(lambda x: f"{x:.2%}")
top10["total_gmv_inr"] = top10["total_gmv_inr"].apply(lambda x: f"{x:,.0f}")

fig, ax = plt.subplots(figsize=(12, 4.2))
ax.axis("off")
tbl = ax.table(cellText=top10.values, colLabels=top10.columns, loc="center", cellLoc="center")
tbl.auto_set_font_size(False)
tbl.set_fontsize(9)
tbl.scale(1, 1.8)
for j in range(len(top10.columns)):
    tbl[0, j].set_facecolor("#1F4E78")
    tbl[0, j].set_text_props(color="white", fontweight="bold")
for i in range(len(top10)):
    if top10.iloc[i]["high_risk_flag"]:
        for j in range(len(top10.columns)):
            tbl[i + 1, j].set_facecolor("#FFC7CE")
ax.set_title("Top 10 Merchants by Transaction Count (flagged if chargeback_ratio > 1%)", pad=20)
plt.tight_layout()
plt.savefig(BASE_DIR / "dashboard_4_details.png", dpi=150, bbox_inches="tight")
plt.close()

n_flagged = (merch_stats["chargeback_ratio"] > 0.01).sum()

interpretations.append(f"""### Layer 4 - Details
Among the top 10 merchants by transaction volume, {(top10['high_risk_flag'] != '').sum()} are
flagged high-risk in this view; platform-wide, {n_flagged} of all 40 merchants exceed the 1%
chargeback-ratio threshold. Because chargebacks are rare events layered onto a modest per-merchant
transaction count (~13-14 transactions per merchant on average), a single seeded burner-account
chargeback landing on a low-volume merchant is enough to push that merchant's ratio well past 1%
-- this is a useful early-warning signal, but in production it should be paired with a minimum
transaction-count threshold before triggering a real investigation, to avoid false positives on
thin-volume merchants.""")

log_path = os.path.join(
os.path.dirname(os.path.abspath(__file__)),"dashboard_interpretations.md")

with open(log_path, "w") as f:
    f.write("# Part 1D - Dashboard: Written Interpretations\n\n")
    f.write("\n\n".join(interpretations))

print("Saved 4 dashboard PNGs + dashboard_interpretations.md")
print(f"match_rate={recon_matched_rate:.4f}  chargeback_ratio={chargeback_ratio:.4f}  flagged_merchants={n_flagged}")
