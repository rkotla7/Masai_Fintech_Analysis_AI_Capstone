"""
Part 3D -- DCF valuation calculator for a hypothetical Paytm business line.

All inputs below are illustrative assumptions chosen for this exercise and
stated explicitly (never hidden magic numbers). Amounts in INR crore.

Produces a 5-year FCFF projection, terminal value,
WACC, a 3x3 sensitivity grid, and an EV/EBITDA cross-check.
"""
import os
from stock_universe import STOCK_UNIVERSE, RISK_FREE_RATE, MARKET_RETURN

# ---------------------------------------------------------------
# Stated inputs (illustrative, for a hypothetical Paytm business line, in INR crore)
# ---------------------------------------------------------------
EBIT_INR_CR = 120.0          # Year-0 EBIT
TAX_RATE = 0.25
DA_INR_CR = 30.0             # Depreciation & Amortization
CAPEX_INR_CR = 45.0          # Capital expenditure
DELTA_NWC_INR_CR = 10.0      # Change in net working capital

GROWTH_YEAR1_5 = [0.18, 0.16, 0.14, 0.12, 0.10]  # fading 5-year growth rate on FCFF
TERMINAL_GROWTH = 0.055      # terminal growth rate (chosen >= 3pp below base WACC, see below)

# WACC inputs
EQUITY_BETA = STOCK_UNIVERSE["PAYFIN"]["beta"]   # use PAYFIN's beta as the business-line proxy
COST_OF_EQUITY = RISK_FREE_RATE + EQUITY_BETA * (MARKET_RETURN - RISK_FREE_RATE)  # CAPM
PRE_TAX_COST_OF_DEBT = 0.095       # illustrative
AFTER_TAX_COST_OF_DEBT = PRE_TAX_COST_OF_DEBT * (1 - TAX_RATE)
WEIGHT_EQUITY = 0.70
WEIGHT_DEBT = 0.30
BASE_WACC = WEIGHT_EQUITY * COST_OF_EQUITY + WEIGHT_DEBT * AFTER_TAX_COST_OF_DEBT

# EV/EBITDA cross-check inputs
ILLUSTRATIVE_EBITDA_INR_CR = EBIT_INR_CR + DA_INR_CR  # EBITDA = EBIT + D&A
ILLUSTRATIVE_EV_EBITDA_MULTIPLE = 9.5


def base_fcff():
    """FCFF = EBIT*(1-tax) + D&A - CapEx - Delta NWC"""
    return EBIT_INR_CR * (1 - TAX_RATE) + DA_INR_CR - CAPEX_INR_CR - DELTA_NWC_INR_CR


def project_fcff(base, growth_rates):
    fcffs = []
    prev = base
    for g in growth_rates:
        nxt = prev * (1 + g)
        fcffs.append(nxt)
        prev = nxt
    return fcffs


def dcf_valuation(wacc, terminal_growth, growth_rates=GROWTH_YEAR1_5):
    base = base_fcff()
    fcffs = project_fcff(base, growth_rates)
    pv_fcffs = [fc / ((1 + wacc) ** (i + 1)) for i, fc in enumerate(fcffs)]

    terminal_value = fcffs[-1] * (1 + terminal_growth) / (wacc - terminal_growth)
    pv_terminal_value = terminal_value / ((1 + wacc) ** len(fcffs))

    enterprise_value = sum(pv_fcffs) + pv_terminal_value
    return {
        "base_fcff": base,
        "projected_fcff": fcffs,
        "pv_fcffs": pv_fcffs,
        "terminal_value": terminal_value,
        "pv_terminal_value": pv_terminal_value,
        "enterprise_value": enterprise_value,
    }


if __name__ == "__main__":
    print(f"Cost of equity (CAPM, beta={EQUITY_BETA}): {COST_OF_EQUITY:.4%}")
    print(f"After-tax cost of debt: {AFTER_TAX_COST_OF_DEBT:.4%}")
    print(f"Base-case WACC: {BASE_WACC:.4%}")
    print(f"Terminal growth rate: {TERMINAL_GROWTH:.2%}")
    print(f"WACC - terminal growth (base case): {BASE_WACC - TERMINAL_GROWTH:.4%}\n")

    base_result = dcf_valuation(BASE_WACC, TERMINAL_GROWTH)
    print(f"Base FCFF (year 0): INR {base_result['base_fcff']:.2f} cr")
    print(f"5-year projected FCFF: {[round(x,2) for x in base_result['projected_fcff']]}")
    print(f"Terminal value: INR {base_result['terminal_value']:.2f} cr")
    print(f"PV of terminal value: INR {base_result['pv_terminal_value']:.2f} cr")
    print(f"Enterprise Value (base case): INR {base_result['enterprise_value']:.2f} cr\n")

    # --- 3x3 sensitivity grid: WACC (-1pp, base, +1pp is not required--spec says -1pp on
    # one axis) x terminal growth (+1pp on other axis). We build the full ±1pp x ±1pp
    # grid (3x3) as requested: WACC in {base-1pp, base, base+1pp}, growth in
    # {term-1pp, term, term+1pp}, and confirm WACC > growth in all 9 cells.
    wacc_grid = [BASE_WACC - 0.01, BASE_WACC, BASE_WACC + 0.01]
    growth_grid = [TERMINAL_GROWTH - 0.01, TERMINAL_GROWTH, TERMINAL_GROWTH + 0.01]

    print("3x3 Sensitivity Table (Enterprise Value, INR cr)")
    header = "WACC \\ Growth".ljust(16) + "".join(f"{g:.2%}".rjust(12) for g in growth_grid)
    print(header)
    sensitivity_rows = []
    min_gap = 999
    for w in wacc_grid:
        row_vals = []
        row_str = f"{w:.2%}".ljust(16)
        for g in growth_grid:
            res = dcf_valuation(w, g)
            ev = res["enterprise_value"]
            row_vals.append(ev)
            row_str += f"{ev:,.1f}".rjust(12)
            min_gap = min(min_gap, w - g)
        sensitivity_rows.append((w, row_vals))
        print(row_str)

    print(f"\nWorst-case WACC - terminal growth across all 9 cells: {min_gap:.4%} "
          f"(must be >= 1 percentage point)")
    assert min_gap >= 0.01, "Sensitivity grid violates the >=1pp WACC-over-growth constraint!"
    print("Self-check PASSED: WACC exceeds terminal growth by >= 1pp in every one of the 9 cells.\n")

    # --- EV/EBITDA cross-check ---
    ev_ebitda_estimate = ILLUSTRATIVE_EBITDA_INR_CR * ILLUSTRATIVE_EV_EBITDA_MULTIPLE
    print(f"EV/EBITDA cross-check: EBITDA = INR {ILLUSTRATIVE_EBITDA_INR_CR:.2f} cr, "
          f"multiple = {ILLUSTRATIVE_EV_EBITDA_MULTIPLE}x -> EV estimate = "
          f"INR {ev_ebitda_estimate:,.2f} cr")
    print(f"DCF-based EV (base case): INR {base_result['enterprise_value']:,.2f} cr")

    diff_pct = (base_result['enterprise_value'] - ev_ebitda_estimate) / ev_ebitda_estimate
    comparison_note = (
        f"The DCF-based enterprise value (INR {base_result['enterprise_value']:,.1f} cr) is "
        f"{'higher' if diff_pct > 0 else 'lower'} than the EV/EBITDA multiple-based estimate "
        f"(INR {ev_ebitda_estimate:,.1f} cr) by {abs(diff_pct):.1%}. This gap is expected: the "
        f"DCF is sensitive to the fading 10-18% growth assumption baked into the 5-year "
        f"projection, while the EV/EBITDA multiple is a single-year snapshot that implicitly "
        f"assumes the business trades in line with comparable peers rather than its own "
        f"forward growth trajectory -- in practice both are used together as a sanity check "
        f"on each other rather than either being taken as the sole 'true' value."
    )
    print("\n" + comparison_note)

    log_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "dcf_report.md")

    with open(log_path, "w") as f:
        f.write("# Part 3D - DCF Valuation Report\n\n")
        f.write("## Inputs (stated)\n")
        f.write(f"- Base EBIT: INR {EBIT_INR_CR} cr | Tax rate: {TAX_RATE:.0%} | D&A: INR {DA_INR_CR} cr | "
                f"CapEx: INR {CAPEX_INR_CR} cr | Delta NWC: INR {DELTA_NWC_INR_CR} cr\n")
        f.write(f"- FCFF formula: EBIT x (1 - tax) + D&A - CapEx - Delta NWC\n")
        f.write(f"- 5-year fading growth rates: {[f'{g:.0%}' for g in GROWTH_YEAR1_5]}\n")
        f.write(f"- Terminal growth rate: {TERMINAL_GROWTH:.2%}\n")
        f.write(f"- Cost of equity (CAPM, beta={EQUITY_BETA} from PAYFIN): {COST_OF_EQUITY:.4%}\n")
        f.write(f"- After-tax cost of debt: {AFTER_TAX_COST_OF_DEBT:.4%} "
                f"(pre-tax {PRE_TAX_COST_OF_DEBT:.2%})\n")
        f.write(f"- Capital structure: {WEIGHT_EQUITY:.0%} equity / {WEIGHT_DEBT:.0%} debt\n")
        f.write(f"- **Base-case WACC: {BASE_WACC:.4%}**\n\n")

        f.write("## Base-case DCF result\n")
        f.write(f"- Base FCFF (year 0): INR {base_result['base_fcff']:.2f} cr\n")
        f.write(f"- 5-year projected FCFF: {[round(x,2) for x in base_result['projected_fcff']]}\n")
        f.write(f"- Terminal value: INR {base_result['terminal_value']:,.2f} cr\n")
        f.write(f"- PV of terminal value: INR {base_result['pv_terminal_value']:,.2f} cr\n")
        f.write(f"- **Enterprise Value (base case): INR {base_result['enterprise_value']:,.2f} cr**\n\n")

        f.write("## 3x3 Sensitivity Table (Enterprise Value, INR crore)\n\n")
        f.write("| WACC \\ Growth | " + " | ".join(f"{g:.2%}" for g in growth_grid) + " |\n")
        for w, row_vals in sensitivity_rows:
            f.write(f"| {w:.2%} | " + " | ".join(f"{v:,.1f}" for v in row_vals) + " |\n")
        f.write(f"\nWorst-case WACC - terminal growth across all 9 cells: **{min_gap:.4%}** "
                f"(constraint: >= 1 percentage point) -- **PASSED**\n\n")

        f.write("## EV/EBITDA cross-check\n")
        f.write(f"- Illustrative EBITDA: INR {ILLUSTRATIVE_EBITDA_INR_CR:.2f} cr, "
                f"multiple: {ILLUSTRATIVE_EV_EBITDA_MULTIPLE}x\n")
        f.write(f"- EV/EBITDA-implied EV: INR {ev_ebitda_estimate:,.2f} cr\n\n")
        f.write(comparison_note + "\n")

    print(f"\nSaved {log_path}")
