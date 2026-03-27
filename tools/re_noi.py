#!/usr/bin/env python3
"""Real estate NOI builder — rent roll to net operating income with projections."""

import argparse


def noi_builder(
    units: int,
    avg_rent_monthly: float,
    occupancy: float = 0.95,
    other_income_pct: float = 0.05,
    opex_ratio: float = 0.40,
    capex_reserve_per_unit: float = 250,
    rent_growth: float = 0.03,
    expense_growth: float = 0.02,
    projection_years: int = 5,
    vacancy_improvement: float = 0,
) -> dict:
    """Build NOI from rent roll fundamentals and project forward.

    Args:
        units: Number of units.
        avg_rent_monthly: Average monthly rent per unit.
        occupancy: Stabilized occupancy rate (e.g., 0.95).
        other_income_pct: Other income as % of gross rent (parking, laundry, etc.).
        opex_ratio: Operating expenses as % of effective gross income.
        capex_reserve_per_unit: Annual capex reserve per unit.
        rent_growth: Annual rent growth rate.
        expense_growth: Annual expense growth rate.
        projection_years: Number of years to project.
        vacancy_improvement: Annual occupancy improvement (e.g., 0.02 per year).

    Returns:
        Dict with Year 1 NOI and multi-year projection.
    """
    if units <= 0:
        raise ValueError("Units must be positive")

    projections = []
    for year in range(projection_years):
        occ = min(occupancy + vacancy_improvement * year, 0.99)
        rent = avg_rent_monthly * (1 + rent_growth) ** year
        gpr = units * rent * 12
        vacancy_loss = gpr * (1 - occ)
        egi = gpr - vacancy_loss
        other_income = gpr * other_income_pct
        total_revenue = egi + other_income

        opex_base = total_revenue * opex_ratio * (1 + expense_growth) ** year
        capex = capex_reserve_per_unit * units * (1 + expense_growth) ** year
        total_expenses = opex_base + capex
        noi = total_revenue - total_expenses

        projections.append(
            {
                "year": year + 1,
                "occupancy": round(occ, 4),
                "avg_rent": round(rent, 2),
                "gross_potential_rent": round(gpr, 2),
                "vacancy_loss": round(vacancy_loss, 2),
                "other_income": round(other_income, 2),
                "effective_gross_income": round(total_revenue, 2),
                "operating_expenses": round(opex_base, 2),
                "capex_reserves": round(capex, 2),
                "noi": round(noi, 2),
            }
        )

    year1 = projections[0]
    noi_cagr = 0
    if len(projections) > 1 and projections[0]["noi"] > 0:
        n = len(projections) - 1
        noi_cagr = (projections[-1]["noi"] / projections[0]["noi"]) ** (1 / n) - 1

    return {
        "year_1_noi": year1["noi"],
        "year_1_opex_ratio": round(year1["operating_expenses"] / year1["effective_gross_income"], 4)
        if year1["effective_gross_income"] > 0
        else 0,
        "noi_per_unit": round(year1["noi"] / units, 2),
        "rent_per_sf_equiv": round(avg_rent_monthly, 2),
        "noi_cagr": round(noi_cagr, 4),
        "projections": projections,
        "breakeven_occupancy": round(
            (year1["operating_expenses"] + year1["capex_reserves"])
            / (year1["gross_potential_rent"] + year1["other_income"]),
            4,
        )
        if (year1["gross_potential_rent"] + year1["other_income"]) > 0
        else 0,
    }


def main():
    parser = argparse.ArgumentParser(description="RE NOI Builder")
    parser.add_argument("--units", type=int, required=True, help="Number of units")
    parser.add_argument("--rent", type=float, required=True, help="Avg monthly rent/unit")
    parser.add_argument("--occupancy", type=float, default=0.95, help="Occupancy (default 0.95)")
    parser.add_argument("--opex-ratio", type=float, default=0.40, help="OpEx ratio (default 0.40)")
    parser.add_argument("--rent-growth", type=float, default=0.03, help="Rent growth (default 3%%)")
    parser.add_argument("--years", type=int, default=5, help="Projection years")
    args = parser.parse_args()
    r = noi_builder(
        args.units,
        args.rent,
        args.occupancy,
        opex_ratio=args.opex_ratio,
        rent_growth=args.rent_growth,
        projection_years=args.years,
    )
    print(f"\n{'=' * 60}")
    print("  NOI Build-Up & Projection")
    print(f"{'=' * 60}")
    print(f"  Units: {args.units}  |  Avg Rent: ${args.rent:,.0f}/mo  |  Occupancy: {args.occupancy * 100:.0f}%")
    print(f"  Year 1 NOI: ${r['year_1_noi']:>,.0f}  |  NOI/Unit: ${r['noi_per_unit']:>,.0f}")
    print(f"  Breakeven Occupancy: {r['breakeven_occupancy'] * 100:.1f}%")
    print(f"{'─' * 60}")
    print(f"  {'Year':>4}  {'Occ':>5}  {'Rent':>8}  {'EGI':>12}  {'OpEx':>12}  {'NOI':>12}")
    for p in r["projections"]:
        print(
            f"  {p['year']:>4}  {p['occupancy'] * 100:>4.0f}%  ${p['avg_rent']:>6,.0f}"
            f"  ${p['effective_gross_income']:>11,.0f}  ${p['operating_expenses']:>11,.0f}  ${p['noi']:>11,.0f}"
        )
    print(f"{'─' * 60}")
    print(f"  NOI CAGR: {r['noi_cagr'] * 100:.1f}%")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
