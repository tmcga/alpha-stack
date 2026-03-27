#!/usr/bin/env python3
"""IRR/NPV solver — general-purpose for any cash flow stream."""

import argparse


def irr_solve(cash_flows: list[float], guess: float = 0.10) -> dict:
    """Calculate IRR using Newton's method, plus NPV at multiple discount rates.

    Args:
        cash_flows: Cash flow stream where index 0 is time 0 (typically negative).
        guess: Initial IRR guess (default 0.10).

    Returns:
        Dict with IRR, NPV at various rates, payback period, and MOIC.
    """
    if not cash_flows:
        raise ValueError("Cash flows must not be empty")
    if all(c >= 0 for c in cash_flows) or all(c <= 0 for c in cash_flows):
        return {"error": "Cash flows must have at least one sign change", "irr": None}

    # Newton's method for IRR
    r = guess
    converged = False
    for _ in range(300):
        npv = sum(c / (1 + r) ** t for t, c in enumerate(cash_flows))
        dnpv = sum(-t * c / (1 + r) ** (t + 1) for t, c in enumerate(cash_flows))
        if abs(dnpv) < 1e-14:
            break
        r_new = r - npv / dnpv
        r_new = max(-0.99, min(r_new, 100.0))
        if abs(r_new - r) < 1e-10:
            converged = True
            break
        r = r_new

    irr = r if converged else None

    # NPV at standard discount rates
    npv_table = {}
    for rate in [0.0, 0.05, 0.08, 0.10, 0.12, 0.15, 0.20]:
        npv_table[f"{rate:.0%}"] = round(sum(c / (1 + rate) ** t for t, c in enumerate(cash_flows)), 2)

    # MOIC
    invested = sum(abs(c) for c in cash_flows if c < 0)
    returned = sum(c for c in cash_flows if c > 0)
    moic = returned / invested if invested > 0 else 0

    # Payback period
    cumulative = 0
    payback = None
    for t, c in enumerate(cash_flows):
        cumulative += c
        if cumulative >= 0 and payback is None and t > 0:
            # Interpolate within the year
            prev = cumulative - c
            payback = t - 1 + abs(prev) / c if c > 0 else t
            break

    return {
        "irr": round(irr, 6) if irr is not None else None,
        "converged": converged,
        "moic": round(moic, 3),
        "payback_years": round(payback, 2) if payback is not None else None,
        "npv_table": npv_table,
        "total_invested": round(invested, 2),
        "total_returned": round(returned, 2),
        "cash_flows": cash_flows,
    }


def npv(cash_flows: list[float], discount_rate: float) -> dict:
    """Calculate Net Present Value at a given discount rate.

    Args:
        cash_flows: Cash flow stream.
        discount_rate: Discount rate.

    Returns:
        Dict with NPV, PV of each cash flow.
    """
    pvs = [round(c / (1 + discount_rate) ** t, 2) for t, c in enumerate(cash_flows)]
    return {
        "npv": round(sum(pvs), 2),
        "discount_rate": discount_rate,
        "present_values": pvs,
    }


def main():
    parser = argparse.ArgumentParser(description="IRR/NPV Solver")
    parser.add_argument("--cfs", required=True, help="Comma-separated cash flows (time 0 first)")
    parser.add_argument("--rate", type=float, default=None, help="Discount rate for NPV (optional)")
    args = parser.parse_args()

    cfs = [float(x.strip()) for x in args.cfs.split(",")]
    r = irr_solve(cfs)

    print(f"\n{'=' * 50}")
    print("  IRR / NPV Analysis")
    print(f"{'=' * 50}")
    if r["irr"] is not None:
        print(f"  IRR:             {r['irr'] * 100:>10.2f}%")
    else:
        print(f"  IRR:             {'N/A':>10s}")
    print(f"  MOIC:            {r['moic']:>10.2f}x")
    if r["payback_years"] is not None:
        print(f"  Payback:         {r['payback_years']:>10.1f} years")
    print(f"  Total Invested:  ${r['total_invested']:>10,.0f}")
    print(f"  Total Returned:  ${r['total_returned']:>10,.0f}")
    print(f"{'─' * 50}")
    print("  NPV Sensitivity:")
    for rate_label, npv_val in r["npv_table"].items():
        print(f"    at {rate_label:>4s}:  ${npv_val:>12,.2f}")
    print(f"{'=' * 50}\n")

    if args.rate is not None:
        n = npv(cfs, args.rate)
        print(f"  NPV at {args.rate:.1%}: ${n['npv']:>,.2f}\n")


if __name__ == "__main__":
    main()
