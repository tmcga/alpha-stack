# Rolling Forecast

Prompt library for building and maintaining rolling forecasts. Covers revenue forecasting, driver-based models, and variance analysis for operational planning.

## Role Context

```
You are a financial planning analyst who builds forecasts that are useful for
decision-making, not just compliance. You know that forecast accuracy matters less
than forecast utility — a model that clearly identifies the 3-4 drivers that
determine outcomes is more valuable than a precise but opaque spreadsheet.
```

---

## 1. Revenue Forecast Model

```
Build a rolling revenue forecast for [company name] in [industry].

Historical data:
| Month | Revenue | New Customers | Churned | Avg Deal Size | Pipeline |
|-------|---------|--------------|---------|--------------|----------|
| [M-6] | $[X] | [N] | [N] | $[X] | $[X] |
| [M-5] | $[X] | [N] | [N] | $[X] | $[X] |
| ... through current month |

Business model: [subscription/transactional/hybrid]

Build a [6/12]-month forward forecast:
1. **Driver decomposition**: Revenue = Existing Customer Revenue + New Customer Revenue - Churned Revenue
2. **New customer model**: Pipeline × Win Rate × Avg Deal Size
3. **Expansion model**: Existing Customers × NRR or Upsell Rate
4. **Seasonality adjustment**: Identify and apply seasonal patterns from historical data
5. **Three scenarios**: Base (most likely), Upside (+[X]%), Downside (-[X]%)
6. **Key assumptions table**: List every assumption, label confidence level
```

## 2. Variance Analysis

```
I need a variance analysis for [company name] for [period].

Actual vs. forecast:
| Line Item | Forecast | Actual | Variance ($) | Variance (%) |
|-----------|----------|--------|-------------|-------------|
| Revenue | $[X] | $[X] | | |
| COGS | $[X] | $[X] | | |
| Gross Profit | $[X] | $[X] | | |
| S&M | $[X] | $[X] | | |
| R&D | $[X] | $[X] | | |
| G&A | $[X] | $[X] | | |
| EBITDA | $[X] | $[X] | | |

Analyze:
1. **Materiality filter**: Flag variances > [X]% or > $[X]K
2. **Root cause decomposition**: Volume vs. price vs. mix vs. timing for revenue; headcount vs. spend-per-head for opex
3. **Controllable vs. uncontrollable**: Separate variances management can influence from external factors
4. **Forecast accuracy score**: MAPE for each line item over last [4-6] periods
5. **Bias detection**: Is the forecast consistently over or under? By how much?
6. **Recommendation**: Which assumptions need recalibration?
```

---

See also: `/budget`, `/fpa`, `/board-deck`
