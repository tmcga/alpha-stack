#!/usr/bin/env python3
"""Real estate development pro forma — ground-up construction analysis."""

import argparse


def development_proforma(
    land_cost: float,
    hard_costs: float,
    soft_cost_pct: float = 0.20,
    contingency_pct: float = 0.05,
    construction_months: int = 18,
    lease_up_months: int = 6,
    construction_rate: float = 0.07,
    stabilized_noi: float = 0,
    exit_cap_rate: float = 0.055,
    equity_pct: float = 0.35,
    perm_rate: float = 0.065,
    perm_amort: int = 30,
) -> dict:
    """Build a development pro forma from land through stabilization.

    Args:
        land_cost: Land acquisition cost.
        hard_costs: Construction hard costs (total).
        soft_cost_pct: Soft costs as % of hard costs (arch, eng, legal, permits).
        contingency_pct: Contingency as % of hard + soft costs.
        construction_months: Construction period in months.
        lease_up_months: Lease-up period after construction.
        construction_rate: Construction loan interest rate.
        stabilized_noi: Annual NOI at stabilization.
        exit_cap_rate: Cap rate for residual value calculation.
        equity_pct: Developer equity as % of total cost.
        perm_rate: Permanent loan interest rate.
        perm_amort: Permanent loan amortization in years.

    Returns:
        Dict with total development cost, margins, yields, and returns.
    """
    soft_costs = hard_costs * soft_cost_pct
    subtotal = hard_costs + soft_costs
    contingency = subtotal * contingency_pct
    hard_soft_contingency = subtotal + contingency

    # Construction interest — assume average outstanding of 60% of costs over construction period
    avg_draw = (land_cost + hard_soft_contingency) * 0.60
    construction_interest = avg_draw * construction_rate * (construction_months / 12)

    total_dev_cost = land_cost + hard_soft_contingency + construction_interest

    # Yield on cost
    yield_on_cost = stabilized_noi / total_dev_cost if total_dev_cost > 0 else 0

    # Development spread (yield on cost - exit cap rate)
    dev_spread = yield_on_cost - exit_cap_rate

    # Stabilized value
    stabilized_value = stabilized_noi / exit_cap_rate if exit_cap_rate > 0 else 0

    # Profit metrics
    profit = stabilized_value - total_dev_cost
    margin = profit / stabilized_value if stabilized_value > 0 else 0
    profit_on_cost = profit / total_dev_cost if total_dev_cost > 0 else 0

    # Capital structure
    equity = total_dev_cost * equity_pct
    construction_loan = total_dev_cost * (1 - equity_pct)
    ltc = construction_loan / total_dev_cost

    # Permanent financing at stabilization
    perm_loan_max = stabilized_value * 0.70  # 70% LTV
    mr = perm_rate / 12
    n = perm_amort * 12
    if mr > 0:
        perm_ds = perm_loan_max * (mr / (1 - (1 + mr) ** -n)) * 12
    else:
        perm_ds = perm_loan_max / perm_amort
    perm_dscr = stabilized_noi / perm_ds if perm_ds > 0 else 0

    # Developer equity return (simplified)
    total_months = construction_months + lease_up_months
    # Cash flows: -equity at time 0, stabilized_noi in year 1+, sale at exit
    # Simplified: equity return = profit / equity, unlevered
    equity_multiple = (equity + profit) / equity if equity > 0 else 0
    hold_years = total_months / 12
    irr_approx = (equity_multiple ** (1 / hold_years) - 1) if hold_years > 0 and equity_multiple > 0 else -1.0

    return {
        "cost_breakdown": {
            "land": land_cost,
            "hard_costs": hard_costs,
            "soft_costs": round(soft_costs, 2),
            "contingency": round(contingency, 2),
            "construction_interest": round(construction_interest, 2),
            "total_development_cost": round(total_dev_cost, 2),
        },
        "yield_on_cost": round(yield_on_cost, 4),
        "exit_cap_rate": exit_cap_rate,
        "development_spread_bps": round(dev_spread * 10000),
        "stabilized_value": round(stabilized_value, 2),
        "profit": round(profit, 2),
        "margin_on_value": round(margin, 4),
        "profit_on_cost": round(profit_on_cost, 4),
        "construction_loan": round(construction_loan, 2),
        "ltc": round(ltc, 4),
        "equity_required": round(equity, 2),
        "perm_loan": round(perm_loan_max, 2),
        "perm_dscr": round(perm_dscr, 4),
        "equity_multiple": round(equity_multiple, 3),
        "irr_approx": round(irr_approx, 4),
        "timeline_months": total_months,
    }


def main():
    parser = argparse.ArgumentParser(description="RE Development Pro Forma")
    parser.add_argument("--land", type=float, required=True, help="Land cost")
    parser.add_argument("--hard", type=float, required=True, help="Hard costs")
    parser.add_argument("--soft-pct", type=float, default=0.20, help="Soft cost %% of hard")
    parser.add_argument("--noi", type=float, required=True, help="Stabilized annual NOI")
    parser.add_argument("--exit-cap", type=float, default=0.055, help="Exit cap rate")
    parser.add_argument("--months", type=int, default=18, help="Construction months")
    parser.add_argument("--const-rate", type=float, default=0.07, help="Construction loan rate")
    parser.add_argument("--equity-pct", type=float, default=0.35, help="Equity %% of total cost")
    args = parser.parse_args()
    r = development_proforma(
        args.land,
        args.hard,
        args.soft_pct,
        construction_months=args.months,
        construction_rate=args.const_rate,
        stabilized_noi=args.noi,
        exit_cap_rate=args.exit_cap,
        equity_pct=args.equity_pct,
    )
    c = r["cost_breakdown"]
    print(f"\n{'=' * 55}")
    print("  Development Pro Forma")
    print(f"{'=' * 55}")
    print(f"  Land:                  ${c['land']:>12,.0f}")
    print(f"  Hard Costs:            ${c['hard_costs']:>12,.0f}")
    print(f"  Soft Costs:            ${c['soft_costs']:>12,.0f}")
    print(f"  Contingency:           ${c['contingency']:>12,.0f}")
    print(f"  Construction Interest: ${c['construction_interest']:>12,.0f}")
    print(f"  Total Dev Cost:        ${c['total_development_cost']:>12,.0f}")
    print(f"{'─' * 55}")
    print(f"  Stabilized NOI:        ${args.noi:>12,.0f}")
    print(f"  Yield on Cost:         {r['yield_on_cost'] * 100:>11.2f}%")
    print(f"  Exit Cap Rate:         {r['exit_cap_rate'] * 100:>11.2f}%")
    print(f"  Dev Spread:            {r['development_spread_bps']:>9.0f} bps")
    print(f"  Stabilized Value:      ${r['stabilized_value']:>12,.0f}")
    print(f"  Profit:                ${r['profit']:>12,.0f}")
    print(f"  Margin on Value:       {r['margin_on_value'] * 100:>11.1f}%")
    print(f"  Profit on Cost:        {r['profit_on_cost'] * 100:>11.1f}%")
    print(f"{'─' * 55}")
    print(f"  Equity Required:       ${r['equity_required']:>12,.0f}")
    print(f"  Equity Multiple:       {r['equity_multiple']:>11.2f}x")
    print(f"  IRR (approx):          {r['irr_approx'] * 100:>11.1f}%")
    print(f"{'=' * 55}\n")


if __name__ == "__main__":
    main()
