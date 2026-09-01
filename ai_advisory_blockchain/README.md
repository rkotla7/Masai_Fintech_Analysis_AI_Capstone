# Part 3 - AI-Augmented FinTech Advisory & Blockchain Risk

## Setup
```
pip install -r requirements.txt
```

## MOCK_LLM mode
All recorded run transcripts below used **MOCK_LLM left at its default (unset, i.e. mock mode)**
— fully deterministic, rule-based logic, no API key, no network call to any LLM provider.

## Run order
```
python advisory_agent.py       # Part A: think-act-observe portfolio agent, all 5 investors
python extract_disclosure.py   # Part B: structured extraction on all 6 disclosure snippets
python debate.py               # Part C: bull/bear/synthesizer debate demo (ticker: PAYFIN)
python dcf_calculator.py       # Part D: DCF valuation + 3x3 sensitivity grid
```
`blockchain_risk_note.md` (Part E) is a standalone written appendix, no code to run.

## Recorded results (this exact run, MOCK_LLM=1)

### Part A - Advisory agent (see `advisory_agent_results.md` for full transcript)
| Investor | Risk Tier | Allocation | CAPM Return | Portfolio Std Dev | Status |
|---|---|---|---|---|---|
| INV01 | Conservative | PAYBOND/PAYGOLD/PAYRETAIL | 9.20% | **8.44%** | FINALIZED |
| INV02 | Moderate | PAYRETAIL/PAYINFRA/PAYGOLD | 11.30% | **12.57%** | FINALIZED |
| INV03 | Aggressive | PAYTECH/PAYFIN/PAYINFRA | 15.00% | **20.58%** | **ESCALATED_TO_HUMAN_ADVISOR** |
| INV04 | Moderate | PAYRETAIL/PAYINFRA/PAYGOLD | 11.30% | **12.57%** | FINALIZED |
| INV05 | Aggressive | PAYTECH/PAYFIN/PAYINFRA | 15.00% | **20.58%** | **ESCALATED_TO_HUMAN_ADVISOR** |

Matches the expected deterministic pattern exactly (Conservative/Moderate below the 20%
escalation threshold, Aggressive above it).

### Part B - Disclosure extraction (see `extract_disclosure_output.md`)
- doc_02 (litigation) correctly flagged with `risk_flags: ['litigation risk']`
- doc_01 and doc_04 correctly flagged `hedging_detected: True`
- doc_05 (board-approval language) correctly classified `sentiment: 'confident'`

### Part C - Debate demo (see `debate_output.md`)
Ticker chosen: **PAYFIN** (beta 1.35, std_dev 28%, analyst_expected_return 16%). Bull, bear, and
synthesizer arguments all reference these actual numeric values.

### Part D - DCF (see `dcf_report.md` for the full sensitivity table)
- Base-case WACC: **12.71%** (CAPM cost of equity via PAYFIN's beta, blended with an illustrative
  after-tax cost of debt, 70/30 equity/debt weighting)
- Terminal growth: **5.5%** (7.2pp below base WACC)
- Base-case Enterprise Value: **INR 1,353.75 cr**
- 3x3 sensitivity grid: WACC exceeds terminal growth by **at least 5.2 percentage points** in
  every one of the 9 cells (constraint was >=1pp) — self-check passed
- EV/EBITDA cross-check: INR 1,425.0 cr (9.5x on INR 150 cr EBITDA) — DCF estimate is ~5% lower,
  discussed in `dcf_report.md`

### Part E - Blockchain risk note
See `blockchain_risk_note.md` (approx 900 words) — covers stablecoin/DAO governance risk, a specific
crypto-allocation recommendation (2-3% cap, 0% for Conservative profiles), and a T.A.N.G.-
framework analysis of Authority and Need as the two most relevant social-engineering vectors for
a UPI/wallet + lending + wealth platform, each paired with a named bank-side defense.

## Design decisions
- CAPM expected return uses **beta only** (never `analyst_expected_return`), as required.
- Portfolio variance uses the prescribed formula with a flat pairwise correlation rho = 0.3.
- The advisory agent's `get_stock_data(ticker)` function stands in for an external market-data
  API tool call, reading from the local `STOCK_UNIVERSE` dict.
- DCF's WACC uses PAYFIN's beta as a proxy for a hypothetical Paytm lending business line's
  systematic risk; capital structure (70% equity / 30% debt) and after-tax cost of debt (9.5%
  pre-tax) are stated illustrative assumptions.
