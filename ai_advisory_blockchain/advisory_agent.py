"""
Part 3A -- Portfolio advisory agent (agentic think-act-observe pattern).

MOCK_LLM gating: only the final narrative sentence is gated. Left unset or
set to "1" -> deterministic f-string template (graded baseline, no network
call). Set to "0" -> optional extension calls an LLM to phrase the same
numbers (not required, not used for grading)
.
"""
import os
import math
from stock_universe import STOCK_UNIVERSE, RISK_FREE_RATE, MARKET_RETURN
from investor_profiles import INVESTOR_PROFILES

MOCK_LLM = os.environ.get("MOCK_LLM", "1") == "1"

# Prescribed allocation lookup table (exact, not free-choice)
ALLOCATION_TABLE = {
    "Conservative": ["PAYBOND", "PAYGOLD", "PAYRETAIL"],
    "Moderate": ["PAYRETAIL", "PAYINFRA", "PAYGOLD"],
    "Aggressive": ["PAYTECH", "PAYFIN", "PAYINFRA"],
}
CORRELATION_RHO = 0.3


def think(investor_profile: dict) -> list:
    """THINK stage: decide the allocation for this investor's risk_tolerance tier."""
    risk_tolerance = investor_profile["risk_tolerance"]
    tickers = ALLOCATION_TABLE[risk_tolerance]
    return tickers


def get_stock_data(ticker: str) -> dict:
    """ACT stage (tool call): simulates an external API call to fetch stock stats.
    In production this would hit a real market-data API; here it looks up the local
    STOCK_UNIVERSE dict, which stands in for that external tool."""
    return STOCK_UNIVERSE[ticker]


def act(tickers: list) -> dict:
    """ACT stage: call the get_stock_data tool for every ticker in the allocation."""
    return {ticker: get_stock_data(ticker) for ticker in tickers}


def observe_and_decide(tickers: list, stock_data: dict, weights=None):
    """OBSERVE -> DECIDE stage: compute CAPM expected return + portfolio variance/std,
    and apply the human-in-the-loop escalation rule."""
    if weights is None:
        weights = {t: 1 / len(tickers) for t in tickers}  # equal-weight (1/3 each)

    # CAPM expected return per stock: E(R) = Rf + beta * (Rm - Rf)  -- beta ONLY
    capm_returns = {
        t: RISK_FREE_RATE + stock_data[t]["beta"] * (MARKET_RETURN - RISK_FREE_RATE)
        for t in tickers
    }
    portfolio_return = sum(weights[t] * capm_returns[t] for t in tickers)

    # Portfolio variance: Var(Rp) = sum(wi^2 * sigma_i^2) + 2*sum_{i<j}(wi*wj*Cov(i,j))
    # Cov(i,j) = rho * sigma_i * sigma_j, rho = 0.3 for every pair
    variance = 0.0
    for t in tickers:
        sigma_i = stock_data[t]["std_dev"]
        variance += (weights[t] ** 2) * (sigma_i ** 2)
    for i in range(len(tickers)):
        for j in range(i + 1, len(tickers)):
            ti, tj = tickers[i], tickers[j]
            cov_ij = CORRELATION_RHO * stock_data[ti]["std_dev"] * stock_data[tj]["std_dev"]
            variance += 2 * weights[ti] * weights[tj] * cov_ij

    portfolio_std = math.sqrt(variance)

    escalated = portfolio_std > 0.20
    return {
        "capm_returns": capm_returns,
        "portfolio_return": portfolio_return,
        "portfolio_variance": variance,
        "portfolio_std": portfolio_std,
        "escalated": escalated,
    }


def build_narrative(investor_id, risk_tolerance, tickers, decision):
    if MOCK_LLM:
        return (f"For {risk_tolerance} investor {investor_id}, we recommend an allocation "
                f"across {tickers} with an expected portfolio return of "
                f"{decision['portfolio_return']:.1%} and volatility of "
                f"{decision['portfolio_std']:.1%}.")
    else:
        # Optional MOCK_LLM=0 extension: would call an LLM here to phrase the same
        # numbers more naturally. Not exercised in the graded baseline run.
        raise NotImplementedError("MOCK_LLM=0 path is an optional, ungraded extension.")


def run_agent_for_investor(investor_profile: dict) -> dict:
    investor_id = investor_profile["investor_id"]
    risk_tolerance = investor_profile["risk_tolerance"]

    tickers = think(investor_profile)                 # THINK
    stock_data = act(tickers)                          # ACT (tool call)
    decision = observe_and_decide(tickers, stock_data)  # OBSERVE -> DECIDE

    result = {
        "investor_id": investor_id,
        "risk_tolerance": risk_tolerance,
        "tickers": tickers,
        "portfolio_return": decision["portfolio_return"],
        "portfolio_std": decision["portfolio_std"],
        "escalated": decision["escalated"],
    }

    if decision["escalated"]:
        result["status"] = "ESCALATED_TO_HUMAN_ADVISOR"
        result["narrative"] = (
            f"ESCALATED_TO_HUMAN_ADVISOR: computed portfolio std dev "
            f"({decision['portfolio_std']:.1%}) exceeds the 20% auto-finalize threshold for "
            f"{risk_tolerance} investor {investor_id}. Numbers attached: expected return "
            f"{decision['portfolio_return']:.1%}, allocation {tickers}."
        )
    else:
        result["status"] = "FINALIZED"
        result["narrative"] = build_narrative(investor_id, risk_tolerance, tickers, decision)

    return result


if __name__ == "__main__":
    all_results = []
    for profile in INVESTOR_PROFILES:
        r = run_agent_for_investor(profile)
        all_results.append(r)
        print(f"--- {r['investor_id']} ({r['risk_tolerance']}) ---")
        print(f"  Allocation: {r['tickers']} (equal-weight 1/3 each)")
        print(f"  CAPM portfolio expected return: {r['portfolio_return']:.4%}")
        print(f"  Portfolio std dev: {r['portfolio_std']:.4%}")
        print(f"  Status: {r['status']}")
        print(f"  Narrative: {r['narrative']}\n")

    log_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "advisory_agent_results.md")

    with open(log_path, "w") as f:
        f.write(f"# Part 3A - Advisory Agent Results(MOCK_LLM={MOCK_LLM})\n\n")
        for r in all_results:
            f.write(f"## {r['investor_id']} ({r['risk_tolerance']})\n")
            f.write(f"- Allocation (equal-weight 1/3 each): {r['tickers']}\n")
            f.write(f"- CAPM portfolio expected return: {r['portfolio_return']:.4%}\n")
            f.write(f"- Portfolio std dev: {r['portfolio_std']:.4%}\n")
            f.write(f"- Status: **{r['status']}**\n")
            f.write(f"- Narrative: {r['narrative']}\n\n")
    print(f"Saved {log_path}")
