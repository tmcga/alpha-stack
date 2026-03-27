#!/usr/bin/env python3
"""Real estate equity waterfall — GP/LP promote with multiple hurdle tiers."""

import argparse


def equity_waterfall(
    equity_invested: float,
    cash_flows: list[float],
    lp_share: float = 0.90,
    pref_rate: float = 0.08,
    hurdles: list[dict] | None = None,
) -> dict:
    """Calculate GP/LP distributions through a multi-tier promote waterfall.

    Args:
        equity_invested: Total equity invested (LP + GP combined).
        cash_flows: Annual cash flows available for distribution (after debt service).
        lp_share: LP share of equity (e.g., 0.90 = 90/10 LP/GP).
        pref_rate: Preferred return rate (e.g., 0.08 = 8%).
        hurdles: List of promote tiers, e.g.:
            [{"irr": 0.08, "gp_promote": 0.20}, {"irr": 0.12, "gp_promote": 0.30}]
            If None, uses standard 8%/12% two-tier with 20%/30% promote.

    Returns:
        Dict with per-year distributions, IRR, equity multiple, and promote summary.
    """
    if not hurdles:
        hurdles = [
            {"irr": 0.08, "gp_promote": 0.20},
            {"irr": 0.12, "gp_promote": 0.30},
        ]

    gp_share = 1 - lp_share
    lp_equity = equity_invested * lp_share
    gp_equity = equity_invested * gp_share

    # Track cumulative distributions
    lp_cumulative = 0
    gp_cumulative = 0
    lp_pref_owed = 0
    yearly = []

    for year, cf in enumerate(cash_flows):
        # Accrue pref on unreturned capital
        lp_unreturned = max(lp_equity - lp_cumulative, 0)
        lp_pref_owed += lp_unreturned * pref_rate

        remaining = cf
        lp_dist = 0
        gp_dist = 0

        if remaining > 0:
            # Preferred return to LP
            pref_payment = min(remaining, lp_pref_owed)
            lp_dist += pref_payment
            remaining -= pref_payment
            lp_pref_owed -= pref_payment

        # Remaining distributed per promote tiers
        if remaining > 0:
            lp_base = remaining * lp_share
            gp_base = remaining * gp_share

            # Apply promote — GP gets extra from LP's share above hurdles
            # Simple approach: split remaining by the highest hurdle achieved
            total_dist_so_far = lp_cumulative + gp_cumulative + cf
            em = total_dist_so_far / equity_invested if equity_invested > 0 else 0

            # Determine which tier applies based on cumulative equity multiple
            gp_promote_rate = 0
            for h in hurdles:
                irr_threshold = h["irr"]
                # Approximate: use equity multiple as proxy for IRR tier
                # EM threshold = (1 + IRR)^years for rough mapping
                em_threshold = (1 + irr_threshold) ** (year + 1)
                if em >= em_threshold:
                    gp_promote_rate = h["gp_promote"]

            lp_dist += lp_base * (1 - gp_promote_rate)
            gp_dist += gp_base + lp_base * gp_promote_rate

        lp_cumulative += lp_dist
        gp_cumulative += gp_dist

        yearly.append(
            {
                "year": year + 1,
                "cash_flow": cf,
                "lp_distribution": round(lp_dist, 2),
                "gp_distribution": round(gp_dist, 2),
                "lp_cumulative": round(lp_cumulative, 2),
                "gp_cumulative": round(gp_cumulative, 2),
            }
        )

    lp_multiple = lp_cumulative / lp_equity if lp_equity > 0 else 0
    gp_multiple = gp_cumulative / gp_equity if gp_equity > 0 else 0
    total_multiple = (lp_cumulative + gp_cumulative) / equity_invested if equity_invested > 0 else 0
    total_promote = gp_cumulative - (sum(cash_flows) * gp_share)

    # IRR calculation (Newton's method)
    def _irr(cfs):
        r = 0.10
        for _ in range(200):
            npv = sum(c / (1 + r) ** t for t, c in enumerate(cfs))
            dnpv = sum(-t * c / (1 + r) ** (t + 1) for t, c in enumerate(cfs))
            if abs(dnpv) < 1e-12:
                break
            r -= npv / dnpv
            r = max(-0.99, min(r, 10.0))
        return r

    lp_cfs = [-lp_equity] + [y["lp_distribution"] for y in yearly]
    gp_cfs = [-gp_equity] + [y["gp_distribution"] for y in yearly]
    project_cfs = [-equity_invested] + cash_flows

    return {
        "yearly": yearly,
        "lp_irr": round(_irr(lp_cfs), 4),
        "gp_irr": round(_irr(gp_cfs), 4),
        "project_irr": round(_irr(project_cfs), 4),
        "lp_multiple": round(lp_multiple, 3),
        "gp_multiple": round(gp_multiple, 3),
        "total_multiple": round(total_multiple, 3),
        "total_promote": round(total_promote, 2),
        "lp_equity": lp_equity,
        "gp_equity": gp_equity,
    }


def main():
    parser = argparse.ArgumentParser(description="RE Equity Waterfall")
    parser.add_argument("--equity", type=float, required=True, help="Total equity invested")
    parser.add_argument("--cfs", required=True, help="Comma-separated annual cash flows")
    parser.add_argument("--lp-share", type=float, default=0.90, help="LP share (default 0.90)")
    parser.add_argument("--pref", type=float, default=0.08, help="Pref rate (default 0.08)")
    args = parser.parse_args()
    cfs = [float(x) for x in args.cfs.split(",")]
    r = equity_waterfall(args.equity, cfs, args.lp_share, args.pref)
    print(f"\n{'=' * 60}")
    print("  GP/LP Equity Waterfall")
    print(f"{'=' * 60}")
    print(f"  LP Equity: ${r['lp_equity']:>10,.0f}  |  GP Equity: ${r['gp_equity']:>10,.0f}")
    print(f"{'─' * 60}")
    print(f"  {'Year':>4}  {'Cash Flow':>12}  {'LP Dist':>12}  {'GP Dist':>12}")
    for y in r["yearly"]:
        print(
            f"  {y['year']:>4}  ${y['cash_flow']:>11,.0f}  ${y['lp_distribution']:>11,.0f}  ${y['gp_distribution']:>11,.0f}"
        )
    print(f"{'─' * 60}")
    print(
        f"  LP IRR: {r['lp_irr'] * 100:.1f}%  |  GP IRR: {r['gp_irr'] * 100:.1f}%  |  Project: {r['project_irr'] * 100:.1f}%"
    )
    print(f"  LP Multiple: {r['lp_multiple']:.2f}x  |  GP Multiple: {r['gp_multiple']:.2f}x")
    print(f"  Total Promote to GP: ${r['total_promote']:>,.0f}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
