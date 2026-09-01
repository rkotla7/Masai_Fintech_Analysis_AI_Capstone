# Part 1D - Dashboard: Written Interpretations

### Layer 1 - Headline Scorecards
Total GMV across the 30-day window is INR 382,603 across 547 transactions.
Success rate stands at 85.6%, in line with the ~92% captured rate baked into the
synthetic data, with the remainder split between failures and chargebacks. The reconciliation
match rate of 90.5% reflects that roughly 10% of ledger transactions
have a discrepancy (missing, amount-mismatched, or status-mismatched) versus the gateway export
-- consistent with the ~12% combined injected discrepancy rate. The chargeback ratio of
5.12% is the platform-wide fraud-exposure headline number ops leadership would
watch week over week.

### Layer 2 - Trends
Daily GMV fluctuates around a baseline with no strong weekly seasonality (expected, since the
underlying data is randomly generated rather than day-of-week weighted), peaking on 2026-01-11
at INR 28,284. Chargeback counts are sparse day to day but cluster more heavily
in the back half of the window -- this lines up with how the 15 seeded burner-account frauds
were deliberately injected into days 10-29 of the window rather than spread evenly, so a real
ops team would want to investigate any late-month chargeback uptick specifically for new-account
fraud rather than treating it as generic churn.

### Layer 3 - Breakdown
UPI dominates GMV by payment method (INR 172,274), consistent with
the 55% method-selection weight it was assigned in the data generator and mirroring UPI's real-world
dominance in Indian retail payments. By category, ecommerce contributes the most GMV
(INR 79,896), though with 7 categories roughly evenly represented among 40
merchants the spread across categories is fairly balanced -- there is no single category so
dominant that it represents concentration risk on its own.

### Layer 4 - Details
Among the top 10 merchants by transaction volume, 7 are
flagged high-risk in this view; platform-wide, 20 of all 40 merchants exceed the 1%
chargeback-ratio threshold. Because chargebacks are rare events layered onto a modest per-merchant
transaction count (~13-14 transactions per merchant on average), a single seeded burner-account
chargeback landing on a low-volume merchant is enough to push that merchant's ratio well past 1%
-- this is a useful early-warning signal, but in production it should be paired with a minimum
transaction-count threshold before triggering a real investigation, to avoid false positives on
thin-volume merchants.