# Part 3D - DCF Valuation Report

## Inputs (stated)
- Base EBIT: INR 120.0 cr | Tax rate: 25% | D&A: INR 30.0 cr | CapEx: INR 45.0 cr | Delta NWC: INR 10.0 cr
- FCFF formula: EBIT x (1 - tax) + D&A - CapEx - Delta NWC
- 5-year fading growth rates: ['18%', '16%', '14%', '12%', '10%']
- Terminal growth rate: 5.50%
- Cost of equity (CAPM, beta=1.35 from PAYFIN): 15.1000%
- After-tax cost of debt: 7.1250% (pre-tax 9.50%)
- Capital structure: 70% equity / 30% debt
- **Base-case WACC: 12.7075%**

## Base-case DCF result
- Base FCFF (year 0): INR 65.00 cr
- 5-year projected FCFF: [76.7, 88.97, 101.43, 113.6, 124.96]
- Terminal value: INR 1,829.10 cr
- PV of terminal value: INR 1,005.71 cr
- **Enterprise Value (base case): INR 1,353.75 cr**

## 3x3 Sensitivity Table (Enterprise Value, INR crore)

| WACC \ Growth | 4.50% | 5.50% | 6.50% |
| 11.71% | 1,399.1 | 1,578.5 | 1,826.7 |
| 12.71% | 1,222.8 | 1,353.8 | 1,526.8 |
| 13.71% | 1,085.1 | 1,184.0 | 1,310.3 |

Worst-case WACC - terminal growth across all 9 cells: **5.2075%** (constraint: >= 1 percentage point) -- **PASSED**

## EV/EBITDA cross-check
- Illustrative EBITDA: INR 150.00 cr, multiple: 9.5x
- EV/EBITDA-implied EV: INR 1,425.00 cr

The DCF-based enterprise value (INR 1,353.8 cr) is lower than the EV/EBITDA multiple-based estimate (INR 1,425.0 cr) by 5.0%. This gap is expected: the DCF is sensitive to the fading 10-18% growth assumption baked into the 5-year projection, while the EV/EBITDA multiple is a single-year snapshot that implicitly assumes the business trades in line with comparable peers rather than its own forward growth trajectory -- in practice both are used together as a sanity check on each other rather than either being taken as the sole 'true' value.
