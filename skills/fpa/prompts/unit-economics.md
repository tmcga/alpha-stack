# Unit Economics

Prompt library for FP&A analysts working on unit economics, customer lifetime value, and cohort analysis. Covers SaaS, e-commerce, marketplace, and services business models.

## Role Context

```
You are a strategic finance analyst who thinks in terms of unit economics and
customer cohort behavior. Every business ultimately succeeds or fails at the unit
level — if the economics of acquiring and serving a single customer don't work,
no amount of growth fixes the problem. You decompose P&Ls into per-unit drivers
and build forward models from the bottom up.
```

---

## 1. LTV/CAC Analysis

```
I need a unit economics analysis for [company name] in [industry].

Key metrics:
- Average Contract Value (ACV): $[X]
- Gross margin: [X]%
- Customer acquisition cost (CAC): $[X]
- Logo churn rate (annual): [X]%
- Net revenue retention (NRR): [X]%
- Average customer lifespan: [X] years

Build the complete unit economics framework:

1. **Customer Lifetime Value (LTV)**:
   LTV = ACV × Gross Margin / Churn Rate
   - Adjust for expansion revenue if NRR > 100%
   - Discounted LTV using [X]% discount rate

2. **LTV/CAC Ratio**: Target 3x+ for healthy SaaS
   - Payback period in months: CAC / (ACV × Gross Margin / 12)

3. **Sensitivity table**: LTV/CAC across churn rates ([X-2]% to [X+2]%) and ACV ($[low] to $[high])

4. **Cohort analysis**: Revenue retained by annual cohort over [3-5] years
   - Identify whether early cohorts are better or worse than recent ones
```

## 2. Customer Segmentation Economics

```
I have [N] customers across [2-4] segments for [company name].

Segment data:
| Segment | Customers | ACV | Gross Margin | CAC | Annual Churn | NRR |
|---------|-----------|-----|-------------|-----|-------------|-----|
| [SMB] | [N] | $[X] | [X]% | $[X] | [X]% | [X]% |
| [Mid-Market] | [N] | $[X] | [X]% | $[X] | [X]% | [X]% |
| [Enterprise] | [N] | $[X] | [X]% | $[X] | [X]% | [X]% |

For each segment, calculate:
1. **LTV, LTV/CAC, payback period**
2. **Contribution margin** (revenue - COGS - allocated S&M - allocated CS)
3. **Revenue mix** and **profit mix** — which segments drive revenue vs. profit?
4. **Recommendation**: Where should we invest next GTM dollar? Why?

Model the 3-year ARR impact of shifting [X]% of GTM spend from [segment A] to [segment B].
```

## 3. Cohort Retention Curves

```
I have cohort data for [company name]. Revenue retained by annual cohort:

| Cohort | Year 0 | Year 1 | Year 2 | Year 3 |
|--------|--------|--------|--------|--------|
| [20XX] | $[X]M | $[X]M | $[X]M | $[X]M |
| [20XX] | $[X]M | $[X]M | $[X]M | — |
| [20XX] | $[X]M | $[X]M | — | — |

Analyze:
1. **Gross retention** by cohort (Year 1 / Year 0)
2. **Net retention** by cohort (including expansion)
3. **Trend**: Are newer cohorts retaining better or worse?
4. **Implied steady-state NRR** if current cohort behavior continues
5. **Revenue projection** for next 3 years assuming current cohort dynamics persist
```

---

See also: `/budget`, `/forecast`, `/board-deck`
