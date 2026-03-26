# Variance Analysis

Prompt library for budget-vs-actual variance analysis, decomposition, and corrective action planning.

## Role Context

```
You are an FP&A analyst who investigates variances with the rigor of a forensic
accountant and the judgment of a business partner. Not all variances matter equally.
Your job is to separate signal from noise, identify what is controllable, and
recommend action only where action will change outcomes.
```

---

## 1. Monthly Budget vs. Actual

```
Analyze the monthly budget variance for [company name] for [month/year].

| Line Item | Budget | Actual | Variance $ | Variance % |
|-----------|--------|--------|-----------|-----------|
| Revenue | $[X] | $[X] | | |
| COGS | $[X] | $[X] | | |
| Gross Profit | | | | |
| Sales & Marketing | $[X] | $[X] | | |
| R&D / Engineering | $[X] | $[X] | | |
| G&A | $[X] | $[X] | | |
| EBITDA | | | | |

Materiality threshold: $[X]K or [X]%

For each material variance:
1. **Decomposition**: Break into volume, price, mix, and timing components
2. **Root cause**: One-time event or structural change?
3. **Controllability**: Could management have influenced this?
4. **Trend**: Is this variance consistent with prior months or a new pattern?
5. **Corrective action**: What should change (if anything) going forward?
6. **Forecast impact**: Does this variance change the full-year outlook?
```

## 2. Revenue Variance Deep Dive

```
Deep dive into revenue variance for [company name]:

Revenue components:
| Component | Budget | Actual | Variance |
|-----------|--------|--------|----------|
| New customer revenue | $[X] | $[X] | |
| Expansion revenue | $[X] | $[X] | |
| Renewal revenue | $[X] | $[X] | |
| Churned revenue | -$[X] | -$[X] | |
| Total | $[X] | $[X] | |

Additional context:
- Deals slipped to next month: $[X] ([N] deals)
- Deals pulled forward: $[X] ([N] deals)
- Pricing changes: [describe]
- New product/feature impact: [describe]

Decompose the variance:
1. **Volume effect**: Fewer/more deals than planned × budgeted price
2. **Price effect**: Actual deals × (actual price - budgeted price)
3. **Mix effect**: Different product/segment mix than planned
4. **Timing effect**: Deals that will still close but shifted periods
5. **Permanent vs. temporary**: What revenue is lost vs. delayed?
```

---

See also: `/budget`, `/forecast`, `/fpa`
