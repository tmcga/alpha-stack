#!/usr/bin/env python3
"""Depreciation schedules — straight-line, declining balance, and MACRS."""

import argparse


def straight_line(cost: float, salvage: float, useful_life: int) -> dict:
    """Straight-line depreciation schedule.

    Args:
        cost: Asset cost basis.
        salvage: Salvage value at end of life.
        useful_life: Useful life in years.

    Returns:
        Dict with annual depreciation, schedule, and tax shield estimate.
    """
    if useful_life <= 0:
        raise ValueError("Useful life must be positive")
    depreciable = cost - salvage
    annual = depreciable / useful_life
    schedule = []
    book_value = cost
    for year in range(1, useful_life + 1):
        book_value -= annual
        schedule.append(
            {
                "year": year,
                "depreciation": round(annual, 2),
                "cumulative": round(annual * year, 2),
                "book_value": round(max(book_value, salvage), 2),
            }
        )
    return {
        "method": "straight_line",
        "annual_depreciation": round(annual, 2),
        "depreciable_basis": depreciable,
        "schedule": schedule,
    }


def declining_balance(cost: float, salvage: float, useful_life: int, factor: float = 2.0) -> dict:
    """Double-declining balance (or custom factor) with switch to straight-line.

    Args:
        cost: Asset cost basis.
        salvage: Salvage value.
        useful_life: Useful life in years.
        factor: Acceleration factor (2.0 = double declining, 1.5 = 150% DB).

    Returns:
        Dict with schedule showing annual depreciation and book value.
    """
    if useful_life <= 0:
        raise ValueError("Useful life must be positive")
    rate = factor / useful_life
    schedule = []
    book_value = cost
    cumulative = 0
    for year in range(1, useful_life + 1):
        db_dep = book_value * rate
        remaining_life = useful_life - year + 1
        sl_dep = (book_value - salvage) / remaining_life if remaining_life > 0 else 0
        dep = max(db_dep, sl_dep)  # Switch to SL when it gives more
        dep = min(dep, book_value - salvage)  # Don't go below salvage
        dep = max(dep, 0)
        book_value -= dep
        cumulative += dep
        schedule.append(
            {
                "year": year,
                "depreciation": round(dep, 2),
                "cumulative": round(cumulative, 2),
                "book_value": round(book_value, 2),
            }
        )
    return {"method": f"declining_balance_{factor}x", "schedule": schedule}


# MACRS recovery periods and rates (GDS, half-year convention)
_MACRS = {
    5: [0.2000, 0.3200, 0.1920, 0.1152, 0.1152, 0.0576],
    7: [0.1429, 0.2449, 0.1749, 0.1249, 0.0893, 0.0892, 0.0893, 0.0446],
    15: [
        0.0500,
        0.0950,
        0.0855,
        0.0770,
        0.0693,
        0.0623,
        0.0590,
        0.0590,
        0.0591,
        0.0590,
        0.0591,
        0.0590,
        0.0591,
        0.0590,
        0.0591,
        0.0295,
    ],
    27: None,  # Residential rental — straight-line over 27.5 years
    39: None,  # Nonresidential — straight-line over 39 years
}


def macrs(cost: float, recovery_period: int, bonus_pct: float = 0.0) -> dict:
    """MACRS depreciation with optional bonus depreciation.

    Args:
        cost: Asset cost basis.
        recovery_period: MACRS class life (5, 7, 15, 27, or 39 years).
        bonus_pct: Bonus depreciation percentage (e.g., 0.60 for 60%).

    Returns:
        Dict with schedule, first-year deduction, and tax shield at assumed rate.
    """
    if recovery_period not in _MACRS:
        raise ValueError(f"Recovery period must be one of {list(_MACRS.keys())}")

    bonus = cost * bonus_pct
    remaining_basis = cost - bonus
    rates = _MACRS[recovery_period]

    schedule = []
    if rates is None:
        # Straight-line for 27.5 or 39-year property (mid-month convention)
        life = 27.5 if recovery_period == 27 else 39.0
        annual = remaining_basis / life
        first_year = annual * 0.5  # Half-year approximation
        cumulative = bonus
        for year in range(1, int(life) + 2):
            dep = first_year if year == 1 else annual
            dep = min(dep, remaining_basis - (cumulative - bonus))
            dep = max(dep, 0)
            cumulative += dep
            if dep > 0:
                schedule.append(
                    {
                        "year": year,
                        "depreciation": round(dep, 2),
                        "cumulative": round(cumulative, 2),
                        "book_value": round(cost - cumulative, 2),
                    }
                )
    else:
        cumulative = bonus
        for i, rate in enumerate(rates):
            dep = remaining_basis * rate
            cumulative += dep
            schedule.append(
                {
                    "year": i + 1,
                    "depreciation": round(dep, 2),
                    "cumulative": round(cumulative, 2),
                    "book_value": round(cost - cumulative, 2),
                }
            )

    first_year_total = bonus + (schedule[0]["depreciation"] if schedule else 0)
    tax_rate = 0.25
    return {
        "method": f"macrs_{recovery_period}yr",
        "cost_basis": cost,
        "bonus_depreciation": round(bonus, 2),
        "first_year_deduction": round(first_year_total, 2),
        "first_year_tax_shield": round(first_year_total * tax_rate, 2),
        "schedule": schedule,
    }


def main():
    parser = argparse.ArgumentParser(description="Depreciation Calculator")
    parser.add_argument("--cost", type=float, required=True, help="Asset cost")
    parser.add_argument("--method", choices=["sl", "db", "macrs"], default="sl")
    parser.add_argument("--life", type=int, default=7, help="Useful life / MACRS class")
    parser.add_argument("--salvage", type=float, default=0, help="Salvage value")
    parser.add_argument("--bonus", type=float, default=0, help="Bonus depreciation %%")
    args = parser.parse_args()
    if args.method == "sl":
        r = straight_line(args.cost, args.salvage, args.life)
    elif args.method == "db":
        r = declining_balance(args.cost, args.salvage, args.life)
    else:
        r = macrs(args.cost, args.life, args.bonus)
    print(f"\n{'=' * 55}")
    print(f"  Depreciation: {r['method']}")
    print(f"{'=' * 55}")
    print(f"  {'Year':>4}  {'Depreciation':>14}  {'Cumulative':>12}  {'Book Value':>12}")
    for s in r["schedule"][:15]:
        print(f"  {s['year']:>4}  ${s['depreciation']:>13,.2f}  ${s['cumulative']:>11,.2f}  ${s['book_value']:>11,.2f}")
    if len(r["schedule"]) > 15:
        print(f"  ... ({len(r['schedule']) - 15} more years)")
    print(f"{'=' * 55}\n")


if __name__ == "__main__":
    main()
