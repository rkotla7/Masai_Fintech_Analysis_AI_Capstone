# Blockchain / Crypto Risk Note - "Paytm Crypto Insights" Watchlist

## 1. Stablecoin type and DeFi/DAO governance risk

Before Paytm could responsibly surface a crypto watchlist to retail users, the single most
important distinction to get right is **fiat-collateralized vs. algorithmic stablecoins**. A
fiat-collateralized stablecoin (e.g., one backed 1:1 by cash and short-dated government
securities held with a regulated custodian, with regular attestations) has a materially
different risk profile than an algorithmic stablecoin, which maintains its peg purely through
on-chain incentive mechanisms and a secondary token's supply/demand dynamics rather than a
redeemable reserve asset. Algorithmic stablecoins have a well-documented failure mode: the peg
holds only as long as market confidence in the mechanism holds, and once confidence breaks the
de-peg can be sudden and total, since no external asset backs a 1:1 redemption.
A watchlist feature that displays "stablecoin" next to a token without disclosing which category
it falls into would mislead a retail user into assuming money-market-fund-like safety when the
actual mechanism may carry equity-like or even total-loss risk. At minimum, any stablecoin
surfaced would need a clearly labeled collateral type, custodian/reserve-attestation status (or
explicit "no independent attestation" flag), and historical peg-stability data, not just a price
chart.

The second risk category is **DeFi/DAO governance risk**. Many DeFi protocols and the DAOs that
govern them concentrate effective voting power in a small number of early holders or founding
teams despite a nominally decentralized governance token, so "the protocol is decentralized" is
often more marketing than fact. Smart-contract risk (unaudited code), upgrade-key risk (a small
multisig that can unilaterally change protocol behavior), and treasury risk (a DAO treasury
drainable by a successful malicious proposal) are all real, recurring failure modes here. A
responsible watchlist should surface, at minimum, whether a protocol's contracts have been
independently audited, how concentrated its governance tokens are, and whether upgrades are
time-locked or instantly executable — none of which is visible from a price chart alone.

## 2. Crypto-as-an-asset-class recommendation for Paytm Money

Standard CAPM-style portfolio theory optimizes an efficient frontier over assets with an
expected return grounded in cash flows, dividends, or some claim on future earnings —
cryptocurrency has none of these; its return is driven entirely by future buyers' willingness
to pay more, not by any intrinsic yield. Combined with several other well-documented properties
— low or negative correlation with traditional assets in calm markets that has historically
collapsed toward high positive correlation during liquidity crises (exactly when diversification
benefits are needed most), heavy-tailed and positively-skewed return distributions that make
mean-variance optimization poorly behaved, well-documented survivorship bias in how "crypto
returns" get reported (thousands of tokens have gone to zero and are simply absent from
retrospective performance narratives), and materially higher transaction/custody costs than
listed securities — the standard finding is that crypto does not belong in an optimized
mean-variance portfolio in any meaningful size.

**Recommendation: a maximum allocation of 2-3% of a retail investor's total investable portfolio,
and 0% for any investor in the "Conservative" risk-tolerance tier.** This is not a "zero
allocation" recommendation, because outright exclusion also has a cost — a small, capped sleeve
lets an investor who wants exposure get it without a single bad month being able to meaningfully
damage their financial plan, and a hard cap is easier to enforce and explain than a "just don't"
answer that some users will circumvent anyway on a less-regulated platform. The cap should apply
per-investor at the platform level (not per-transaction), should never be offered to Conservative
or short-horizon (under 3-year) profiles at all given the survivorship-bias and heavy-tail risk
described above, and should come with a mandatory risk disclosure at the point of purchase, not
just in a terms-of-service document.

## 3. T.A.N.G. fraud framework applied to a UPI/wallet + lending + wealth platform

The T.A.N.G. framework (**T**emptation, **A**uthority, **N**eed, **G**reed) names the emotional
levers social engineers pull to get a victim to act against their own interest. For a platform
that combines UPI/wallet payments, lending, and wealth advisory in one app, the two vectors most
relevant to this specific combination of products are:

**Authority.** Because the platform legitimately sends real notifications about loan
approvals, KYC updates, and payment confirmations, users are conditioned to trust
app-branded or bank-branded communication. A fraudster impersonating "Paytm Support" or a
"bank verification officer" asking a user to share a UPI PIN or approve a collect-request "to
verify your account" exploits exactly that conditioned trust, and it is especially effective
immediately after a real lending or KYC event, when a follow-up-looking message feels
contextually plausible rather than suspicious. **Bank-side defense**: real-time collect-request
transaction-intent screening that flags and delays high-risk approval requests (e.g., a
collect-request immediately following a support-impersonation-pattern SMS/call, or requests
above a user's typical transaction size) and requires a stronger, phishing-resistant confirmation
step before releasing funds, rather than a single UPI-PIN tap.

**Need.** The lending product creates a "Need" vector: users seeking urgent credit (often
already in financial stress) are the exact population targeted by fake "instant loan approval,
pay a processing fee first" scams, a well-known fraud pattern in Indian digital lending that
disproportionately targets thin-file / new-to-credit users — the same population Part 2's model
treats with extra care via the `is_thin_file` flag. **Bank-side defense**: real-time checks that
flag any outbound "processing fee" payment request tied to a loan not yet formally approved
through the platform's own lending flow, since legitimate lenders deduct fees from the disbursed
amount rather than demanding an upfront payment.
