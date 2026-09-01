# Part 2 — Credit Risk & Lending ML

Paytm vertical: Postpaid / Lending (BNPL-style consumer and merchant credit).

## Setup
From the repo root: `pip install -r ../requirements.txt`.

## Run order
```bash
cd credit_risk_lending_ml            # must run from this folder — relative paths
python generate_data.py              # regenerates credit_applicants.csv, txn_behaviour.csv (seed 42)
python classification_models.py      # Parts A+B: preprocessing (via eda_preprocessing.get_processed_data),
                                      #   LogReg + DecisionTree, evaluation suite, ROC/confusion-matrix PNGs,
                                      #   risk-pricing table
python anomaly_detection.py          # Part C: IsolationForest anomaly detection + recall check
```
`eda_preprocessing.py` is imported by `classification_models.py`; run it directly if you only want
the EDA printout (default rate, missing %, train-derived median).

## What's in this folder
| File | Task | Notes |
| `generate_data.py` + `credit_applicants.csv`, `txn_behaviour.csv` | Seed data | Seed 42; 400 applicants (measured default rate 20.25%, in the required 15–25% range), exactly 80 (20%) missing `credit_bureau_score`; 265-row behaviour table with 15 seeded anomalies |
| `eda_preprocessing.py` | Part A | Thin-file flag → stratified 75/25 split (`random_state=42`) → train-only median imputation → one-hot encoding → train-only `StandardScaler` |
| `classification_models.py`, `roc_curves.png`, `confusion_matrices.png`, `model_comparison.csv`, `risk_pricing_table.csv` | Part B | Logistic Regression vs. `DecisionTreeClassifier(random_state=42)`, full metric suite, 4-tier risk-pricing table |
| `anomaly_detection.py`, `txn_behaviour_scored.csv` | Part C | `IsolationForest(random_state=42, contamination=15/265)` on standardized behavioural features |

## Design decisions

- **Thin-file handling (order matters):** `is_thin_file` is engineered directly from the raw
  missing/not-missing pattern in `credit_bureau_score` — this is safe pre-split since it depends on
  no fitted statistic. The 75/25 split is stratified on `default` (justified: the ~20% positive
  rate means an unstratified split risks materially skewing the minority class between train/test)
  with `random_state=42`. Only *after* the split is the training-split median of
  `credit_bureau_score` computed and used to fill missing values in both splits — this uses UPI
  inflow and the other alternate-data features already present for these applicants rather than
  discarding them, while never leaking test-set information into the imputation value. No row is
  ever dropped.
- **Encoding/scaling:** `employment_type` is one-hot encoded; all numeric features are scaled with
  `StandardScaler` fit on the training split only, then applied to both splits.
- **Risk-pricing tiers:** quartiles of the logistic regression's predicted default probability,
  each mapped to an illustrative rate band (9–11% / 12–15% / 16–20% / 21–28%). The measured
  observed default rate rises monotonically across tiers: **8% → 12% → 20% → 40%**, confirming the
  pricing bands are correctly ordered by realized risk.
- **Anomaly detection:** contamination is fixed to the known seeded proportion (15/265 ≈ 5.66%)
  rather than tuned, so the reported recall is a clean, honest check against ground truth.

## Model comparison (from the committed run)

| Metric | Logistic Regression | Decision Tree |
| Accuracy | 0.76 | 0.67 |
| Precision | 0.389 | 0.240 |
| Recall | 0.350 | 0.300 |
| F1 | 0.368 | 0.267 |
| AUC | 0.719 | 0.531 |

**Isolation Forest recall:** 11 of the 15 seeded `BTXNA*` anomalies were flagged anomalous —
**73.3% recall** at a contamination rate matched to the true 5.66% seeded proportion.

## Bias-awareness note

Even though this dataset carries no explicit gender or location field, several remaining features
can still act as correlated proxies for a protected attribute once the model is deployed against a
real, more heterogeneous applicant population. **`employment_type`** is the clearest risk: "gig"
work in India skews toward younger applicants and toward certain regions and, in aggregate data,
toward certain caste/religious/migrant-status distributions that correlate with informal-sector
participation — a model that penalizes "gig" status is at real risk of indirectly penalizing those
groups even though it never sees them directly. **`monthly_income_inr`** is a second, well-known
proxy: income is strongly correlated with gender (given persistent wage gaps) and with geography
(urban vs. rural, which in India also correlates with caste and religious composition), so a model
that leans heavily on raw income without controlling for context can systematically under-serve
otherwise-creditworthy applicants from lower-income-correlated groups. **`credit_bureau_score`**
itself is a proxy of proxies — bureau scores are built from historical credit access, and
historical credit access has itself been unevenly distributed across exactly these same groups,
which is precisely why the thin-file population (20% of applicants here) exists in the first place
and why alternate data (UPI inflow) matters as a corrective signal rather than a nice-to-have.

**Recommended governance step before go-live:** a mandatory maker-checker human-in-the-loop review
for every *declined* thin-file applicant (i.e., anyone with `is_thin_file == 1` who the model would
otherwise auto-reject) before the decline is communicated to the customer. This targets governance
effort exactly where the proxy risk above is most concentrated — new-to-credit applicants who the
bureau-based signal can't independently corroborate — without slowing down the majority of
applications that have a bureau score to confirm the model's decision against.

## Final recommendation

Logistic Regression is the recommended model for Paytm Postpaid: it beats the Decision Tree on
every metric that matters for a lending decision — **AUC 0.719 vs. 0.531** (materially better
rank-ordering of risk, which is what the risk-pricing tiers depend on), **accuracy 0.76 vs. 0.67**,
and **precision 0.389 vs. 0.240** (fewer good applicants wrongly declined per flagged default).
Its recall (0.350) is only slightly ahead of the tree's (0.300), so neither model catches most
defaulters outright on this modest 400-row sample — in production this argues for treating the
model's probability output as a risk-based *pricing* input (as the 4-tier table already does,
with a monotonic 8%→40% observed default rate across tiers) rather than as a hard accept/decline
gate on its own. The Decision Tree's much lower AUC and its tendency to overfit small tabular
datasets make it a weaker production candidate here despite being easier to explain rule-by-rule;
if explainability is a hard requirement, a regularized logistic model with SHAP-style coefficient
explanations is preferable to switching to the tree.
