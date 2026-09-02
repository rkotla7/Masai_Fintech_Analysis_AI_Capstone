# Blockchain / Crypto Risk Note - "Paytm Crypto Insights" Watchlist

## 1. Stablecoin type and DeFi/DAO governance risk

The key distinction before surfacing a crypto watchlist to retail users is **fiat-collateralized
vs. algorithmic stablecoins**. A fiat-collateralized stablecoin (backed 1:1 by cash and
short-dated government securities, held by a regulated custodian, with regular attestations)
carries a very different risk profile from an algorithmic stablecoin, which holds its peg purely
through on-chain incentive mechanics rather than a redeemable reserve — and can de-peg suddenly
and totally once market confidence breaks. Labeling both simply as "stablecoin" would mislead a
retail user into assuming money-market-fund-like safety where the real risk may be total loss.
Any stablecoin surfaced needs a labeled collateral type, custodian/attestation status (or an
explicit "no attestation" flag), and historical peg-stability data — not just a price chart.

The second category is **DeFi/DAO governance risk**. Many DeFi protocols concentrate effective
voting power in a handful of early holders or founding teams despite a nominally decentralized
governance token, so "decentralized" is often more marketing than fact. Unaudited smart-contract
code, upgrade-key risk (a small multisig that can unilaterally change protocol behavior), and
treasury risk (a DAO treasury drainable by a malicious proposal) are real, recurring failure
modes. A responsible watchlist should surface contract audit status, governance-token
concentration, and whether upgrades are time-locked — none of which is visible from a price
chart.

## 2. Crypto-as-an-asset-class recommendation for Paytm Money

CAPM-style portfolio theory optimizes over assets whose expected return is grounded in cash
flows, dividends, or a claim on future earnings — cryptocurrency has none of these; its return
depends entirely on future buyers paying more, not intrinsic yield. Its correlation with
traditional assets also spikes higher during liquidity crises, exactly when diversification is
needed most, and its returns are heavy-tailed and positively skewed, which makes mean-variance
optimization poorly behaved. Add well-documented survivorship bias (thousands of tokens have gone
to zero and are simply absent from retrospective return narratives) and higher transaction/
custody costs than listed securities, and the standard finding holds: crypto does not belong in
an optimized mean-variance portfolio in any meaningful size.

**Recommendation: a maximum allocation of 2-3% of a retail investor's total investable portfolio,
and 0% for Conservative risk-tolerance investors.** This isn't a blanket zero — a small, capped
sleeve lets an investor who wants exposure get it without one bad month damaging their financial
plan, and a hard cap is easier to enforce than a "just don't" answer users would circumvent
elsewhere. It applies per-investor at the platform level, excludes Conservative and short-horizon
(under 3-year) profiles entirely, and comes with a mandatory risk disclosure at the point of
purchase, not buried in a terms-of-service document.

## 3. T.A.N.G. fraud framework applied to a UPI/wallet + lending + wealth platform

T.A.N.G. (**T**emptation, **A**uthority, **N**eed, **G**reed) names the emotional levers social
engineers pull to get a victim to act against their own interest. The two most relevant vectors
for a platform combining UPI/wallet payments, lending, and wealth advisory are:

**Authority.** Because the platform legitimately sends real notifications about loan approvals,
KYC updates, and payment confirmations, users are conditioned to trust app- or bank-branded
messages. A fraudster impersonating "Paytm Support," asking a user to share a UPI PIN or approve
a collect-request "to verify your account," exploits that conditioned trust — especially right
after a real lending or KYC event. **Bank-side defense**: real-time collect-request intent
screening that flags and delays high-risk approval requests (e.g., following a
support-impersonation SMS/call, or above a user's typical transaction size) and requires a
phishing-resistant confirmation step before releasing funds, rather than a single UPI-PIN tap.

**Need.** The lending product creates a "Need" vector: users seeking urgent credit, often already
under financial stress, are the exact population targeted by fake "instant loan approval, pay a
processing fee first" scams — a well-known pattern in Indian digital lending that
disproportionately targets thin-file / new-to-credit users, the same population Part 2's model
handles with extra care via the `is_thin_file` flag. **Bank-side defense**: real-time checks that
flag any outbound "processing fee" payment tied to a loan not yet formally approved through the
platform's own lending flow, since legitimate lenders deduct fees from the disbursed amount
rather than demand payment upfront.
