"""
Part 3C -- Multi-agent debate demo (bull / bear / synthesizer) for one
ticker from STOCK_UNIVERSE.

Mock mode (graded baseline): each agent's argument is built from a template
referencing the ticker's actual beta/analyst_expected_return/std_dev, no
LLM call made.
"""
import os
from stock_universe import STOCK_UNIVERSE

MOCK_LLM = os.environ.get("MOCK_LLM", "1") == "1"
CHOSEN_TICKER = "PAYFIN"  # chosen ticker for this debate demo


def bull_agent(ticker: str) -> str:
    d = STOCK_UNIVERSE[ticker]
    return (f"BULL on {ticker}: With an expected return of {d['analyst_expected_return']:.1%} "
            f"against a beta of {d['beta']:.2f}, this offers attractive risk-adjusted upside -- "
            f"the beta above 1.0 means it should outperform in a rising market, and analysts see "
            f"double-digit return potential that justifies the position.")


def bear_agent(ticker: str) -> str:
    d = STOCK_UNIVERSE[ticker]
    return (f"BEAR on {ticker}: A standard deviation of {d['std_dev']:.1%} is high volatility for "
            f"a portfolio holding, and a beta of {d['beta']:.2f} means it will also fall harder "
            f"than the market in a downturn -- the same leverage that drives the bull case cuts "
            f"both ways, and that volatility can erode returns over a shorter investment horizon.")


def synthesizer_agent(ticker: str, bull_text: str, bear_text: str) -> str:
    d = STOCK_UNIVERSE[ticker]
    if MOCK_LLM:
        return (f"SYNTHESIS on {ticker}: {ticker} combines a beta of {d['beta']:.2f} and volatility "
                f"of {d['std_dev']:.1%} with an analyst-expected return of "
                f"{d['analyst_expected_return']:.1%} -- suitable for investors with a higher risk "
                f"tolerance and a longer horizon who can absorb the swings the bear case highlights "
                f"in exchange for the upside the bull case describes. It fits better as a "
                f"satellite position sized to risk tolerance than as a core low-volatility holding.")
    else:
        raise NotImplementedError("MOCK_LLM=0 path is an optional, ungraded extension.")


if __name__ == "__main__":
    print(f"MOCK_LLM = {MOCK_LLM}")
    print(f"Chosen ticker: {CHOSEN_TICKER}\n")

    bull_text = bull_agent(CHOSEN_TICKER)
    bear_text = bear_agent(CHOSEN_TICKER)
    synthesis = synthesizer_agent(CHOSEN_TICKER, bull_text, bear_text)

    print(bull_text, "\n")
    print(bear_text, "\n")
    print(synthesis, "\n")

    log_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "debate_output.md")

    with open(log_path, "w") as f:
        f.write(f"# Part 3C - Multi-Agent Debate (MOCK_LLM={MOCK_LLM})\n\n")
        f.write(f"Ticker: **{CHOSEN_TICKER}** ({STOCK_UNIVERSE[CHOSEN_TICKER]})\n\n")
        f.write(f"## Bull agent\n{bull_text}\n\n")
        f.write(f"## Bear agent\n{bear_text}\n\n")
        f.write(f"## Synthesizer agent\n{synthesis}\n")
    print(f"Saved {log_path}")
