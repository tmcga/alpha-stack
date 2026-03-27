#!/usr/bin/env python3
"""Real estate debt sizing — DSCR, LTV, debt yield, and multi-tranche analysis."""

import argparse


def debt_sizing(
    noi: float,
    property_value: float,
    rate: float,
    amort_years: int = 30,
    max_ltv: float = 0.75,
    min_dscr: float = 1.25,
    max_debt_yield: float | None = None,
    io_years: int = 0,
) -> dict:
    """Size the maximum loan from DSCR, LTV, and debt yield constraints.

    Args:
        noi: Net operating income (annual).
        property_value: Appraised or purchase price.
        rate: Annual interest rate (e.g., 0.065 for 6.5%).
        amort_years: Amortization period in years.
        max_ltv: Maximum loan-to-value ratio.
        min_dscr: Minimum debt service coverage ratio.
        max_debt_yield: Maximum debt yield (NOI/Loan). None to skip.
        io_years: Interest-only period in years (0 = fully amortizing).

    Returns:
        Dict with loan amounts from each constraint and the binding one.
    """
    if noi <= 0:
        raise ValueError("NOI must be positive")
    if rate <= 0:
        raise ValueError("Interest rate must be positive")

    # LTV constraint
    loan_ltv = property_value * max_ltv

    # DSCR constraint — max loan where annual DS / NOI >= min_dscr
    monthly_rate = rate / 12
    n_payments = amort_years * 12
    if monthly_rate > 0:
        pmt_factor = monthly_rate / (1 - (1 + monthly_rate) ** -n_payments)
    else:
        pmt_factor = 1 / n_payments
    max_annual_ds = noi / min_dscr
    loan_dscr = max_annual_ds / (pmt_factor * 12)

    # Debt yield constraint
    loan_dy = noi / max_debt_yield if max_debt_yield else float("inf")

    # Binding constraint
    max_loan = min(loan_ltv, loan_dscr, loan_dy)
    annual_ds = max_loan * pmt_factor * 12
    actual_dscr = noi / annual_ds if annual_ds > 0 else 0
    actual_ltv = max_loan / property_value if property_value > 0 else 0
    actual_dy = noi / max_loan if max_loan > 0 else 0
    mortgage_constant = annual_ds / max_loan if max_loan > 0 else 0

    binding = "ltv"
    if max_loan == loan_dscr:
        binding = "dscr"
    elif max_loan == loan_dy:
        binding = "debt_yield"

    equity = property_value - max_loan
    io_ds = max_loan * rate if io_years > 0 else None
    io_dscr = noi / io_ds if io_ds and io_ds > 0 else None

    return {
        "max_loan": round(max_loan, 2),
        "equity_required": round(equity, 2),
        "binding_constraint": binding,
        "loan_ltv": round(loan_ltv, 2),
        "loan_dscr": round(loan_dscr, 2),
        "loan_debt_yield": round(loan_dy, 2) if loan_dy != float("inf") else None,
        "actual_ltv": round(actual_ltv, 4),
        "actual_dscr": round(actual_dscr, 4),
        "actual_debt_yield": round(actual_dy, 4),
        "annual_debt_service": round(annual_ds, 2),
        "mortgage_constant": round(mortgage_constant, 4),
        "positive_leverage": actual_dy > mortgage_constant,
        "io_annual_ds": round(io_ds, 2) if io_ds else None,
        "io_dscr": round(io_dscr, 4) if io_dscr else None,
    }


def multi_tranche(
    noi: float,
    property_value: float,
    tranches: list[dict],
) -> dict:
    """Analyze multi-tranche capital stack (senior, mezz, preferred).

    Args:
        noi: Net operating income.
        property_value: Property value.
        tranches: List of dicts with keys: name, amount, rate, amort_years (optional).

    Returns:
        Dict with per-tranche metrics and combined stack analysis.
    """
    results = []
    cumulative = 0
    total_ds = 0
    for t in tranches:
        amount = t["amount"]
        r = t["rate"]
        amort = t.get("amort_years", 0)
        cumulative += amount
        if amort > 0 and r > 0:
            mr = r / 12
            n = amort * 12
            ds = amount * (mr / (1 - (1 + mr) ** -n)) * 12
        else:
            ds = amount * r
        total_ds += ds
        ltv = cumulative / property_value if property_value > 0 else 0
        dscr = noi / total_ds if total_ds > 0 else 0
        results.append(
            {
                "name": t.get("name", f"Tranche {len(results) + 1}"),
                "amount": amount,
                "rate": r,
                "annual_ds": round(ds, 2),
                "cumulative_ltv": round(ltv, 4),
                "cumulative_dscr": round(dscr, 4),
            }
        )
    equity = property_value - cumulative
    return {
        "tranches": results,
        "total_debt": cumulative,
        "total_ds": round(total_ds, 2),
        "equity": round(equity, 2),
        "blended_dscr": round(noi / total_ds, 4) if total_ds > 0 else 0,
        "total_ltv": round(cumulative / property_value, 4) if property_value > 0 else 0,
    }


def main():
    parser = argparse.ArgumentParser(description="RE Debt Sizing")
    parser.add_argument("--noi", type=float, required=True, help="Annual NOI")
    parser.add_argument("--value", type=float, required=True, help="Property value")
    parser.add_argument("--rate", type=float, required=True, help="Interest rate")
    parser.add_argument("--amort", type=int, default=30, help="Amort years (default 30)")
    parser.add_argument("--max-ltv", type=float, default=0.75, help="Max LTV (default 0.75)")
    parser.add_argument("--min-dscr", type=float, default=1.25, help="Min DSCR (default 1.25)")
    parser.add_argument("--debt-yield", type=float, default=None, help="Max debt yield")
    args = parser.parse_args()
    r = debt_sizing(
        args.noi,
        args.value,
        args.rate,
        args.amort,
        max_ltv=args.max_ltv,
        min_dscr=args.min_dscr,
        max_debt_yield=args.debt_yield,
    )
    print(f"\n{'=' * 50}")
    print("  RE Debt Sizing")
    print(f"{'=' * 50}")
    print(f"  NOI:               ${args.noi:>12,.0f}")
    print(f"  Property Value:    ${args.value:>12,.0f}")
    print(f"{'─' * 50}")
    print(f"  Max Loan (LTV):    ${r['loan_ltv']:>12,.0f}")
    print(f"  Max Loan (DSCR):   ${r['loan_dscr']:>12,.0f}")
    if r["loan_debt_yield"]:
        print(f"  Max Loan (DY):     ${r['loan_debt_yield']:>12,.0f}")
    print(f"{'─' * 50}")
    print(f"  Binding Constraint: {r['binding_constraint'].upper()}")
    print(f"  Max Loan:          ${r['max_loan']:>12,.0f}")
    print(f"  Equity Required:   ${r['equity_required']:>12,.0f}")
    print(f"  Actual LTV:        {r['actual_ltv'] * 100:>11.1f}%")
    print(f"  Actual DSCR:       {r['actual_dscr']:>11.2f}x")
    print(f"  Debt Yield:        {r['actual_debt_yield'] * 100:>11.2f}%")
    print(f"  Mortgage Constant: {r['mortgage_constant'] * 100:>11.2f}%")
    lev = "YES" if r["positive_leverage"] else "NO"
    print(f"  Positive Leverage: {lev:>11s}")
    print(f"{'=' * 50}\n")


if __name__ == "__main__":
    main()
