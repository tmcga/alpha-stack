# Annual Budget Build

Prompt library for bottom-up annual budget construction. Covers driver-based revenue budgets, departmental expense budgets, and P&L roll-ups.

## Role Context

```
You are a financial planning manager who builds budgets that drive accountability.
A good budget is not a prediction — it is a contract between the business and its
stakeholders about what resources will be deployed and what outcomes are expected.
Every line item traces back to an operational driver that someone owns.
```

---

## 1. Revenue Budget

```
Build a revenue budget for [company name] for fiscal year [20XX].

Current performance:
- Current period revenue: $[X]M ([growth rate]% YoY)
- Revenue mix: [Segment A] [X]%, [Segment B] [X]%, [Segment C] [X]%
- Pricing: Average selling price $[X], trending [up/flat/down]

Revenue drivers by segment:
| Segment | Current Customers | New Pipeline | Win Rate | Avg Deal | Churn |
|---------|------------------|-------------|----------|----------|-------|
| [A] | [N] | $[X]M | [X]% | $[X]K | [X]% |
| [B] | [N] | $[X]M | [X]% | $[X]K | [X]% |

Build:
1. **Monthly revenue by segment** = Existing Base × Retention + New Wins
2. **Bookings to revenue bridge** (if subscription: booking date vs. recognition timing)
3. **Seasonality overlay**: Historical monthly distribution pattern
4. **Board target reconciliation**: How does bottom-up compare to top-down target of $[X]M?
5. **Risk-adjusted view**: Probability-weight pipeline deals by stage
```

## 2. Departmental Expense Budget

```
Build a departmental expense budget for [department] at [company name].

Current state:
- Headcount: [X] employees, planned: [X] by year-end
- Current annual run-rate: $[X]M
- Average fully loaded cost: $[X]K per employee

Expense categories:
| Category | Current Monthly | FY Budget Target | Key Driver |
|----------|---------------|-----------------|-----------|
| Compensation | $[X]K | | Headcount × avg cost |
| Benefits | $[X]K | | [X]% of base salary |
| Contractors | $[X]K | | [project-specific] |
| Software/Tools | $[X]K | | Per-seat licensing |
| Travel | $[X]K | | [events/client visits] |
| Other | $[X]K | | [describe] |

Build:
1. **Monthly expense forecast** with hiring ramp (start dates matter)
2. **Compensation waterfall**: Existing base + merit increases + new hires + backfills
3. **Non-headcount expenses**: Fixed vs. variable vs. discretionary
4. **Cost per unit of output**: What is this department's efficiency metric?
   (e.g., S&M: CAC, CS: cost per customer, Eng: cost per feature shipped)
5. **Variance tolerances**: What deviations trigger re-forecasting?
```

## 3. Zero-Based Budget Review

```
Conduct a zero-based budget review for [department/cost center] at [company name].

Current spend:
| Line Item | Annual Spend | Justification | Owner |
|-----------|-------------|---------------|-------|
| [Item 1] | $[X]K | [reason] | [name] |
| [Item 2] | $[X]K | [reason] | [name] |
| ... | | | |

For each line item:
1. **Necessity test**: What happens if we eliminate this entirely?
2. **Efficiency test**: Can we achieve the same outcome for less?
3. **ROI test**: What is the measurable return on this spend?
4. **Benchmark**: How does this compare to similar companies at our stage?
5. **Decision**: Keep / Reduce / Eliminate / Defer

Target: Identify [X]% savings while maintaining output quality.
```

---

See also: `/forecast`, `/fpa`, `/board-deck`
