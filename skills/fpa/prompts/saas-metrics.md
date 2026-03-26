# SaaS Metrics

Prompt library for SaaS-specific financial analysis. Covers ARR decomposition, magic number, burn multiple, Rule of 40, and benchmarking against stage-appropriate comps.

## Role Context

```
You are a SaaS finance specialist who evaluates businesses through the lens of
recurring revenue quality, capital efficiency, and growth durability. You know that
ARR growth without efficient unit economics is a path to zero, and that the best
SaaS businesses compound through net expansion rather than new logo acquisition.
```

---

## 1. ARR Bridge & Decomposition

```
I need an ARR bridge for [company name] for [quarter/year].

ARR data:
- Beginning ARR: $[X]M
- New business ARR: $[X]M
- Expansion ARR: $[X]M
- Contraction ARR: -$[X]M
- Churned ARR: -$[X]M
- Ending ARR: $[X]M

Build the ARR bridge and calculate:
1. **Gross new ARR** = New + Expansion
2. **Net new ARR** = Gross new - Contraction - Churn
3. **Gross retention rate** = 1 - (Churn / Beginning ARR)
4. **Net retention rate** = (Beginning + Expansion - Contraction - Churn) / Beginning
5. **Expansion rate** = Expansion / Beginning ARR
6. **Trend**: Compare this period to prior [2-4] periods — is net new ARR accelerating?
```

## 2. SaaS Efficiency Metrics

```
Evaluate the capital efficiency of [company name]:

Financial data:
- ARR: $[X]M, growing [X]% YoY
- Gross margin: [X]%
- S&M spend (annual): $[X]M
- Net new ARR (annual): $[X]M
- Operating cash burn: $[X]M/year
- Cash on balance sheet: $[X]M

Calculate and benchmark:
1. **Magic Number** = Net New ARR / Prior Period S&M Spend
   (>0.75 efficient, 0.5-0.75 moderate, <0.5 inefficient)
2. **Burn Multiple** = Net Burn / Net New ARR
   (<1x great, 1-2x good, >2x concerning)
3. **Rule of 40** = Revenue Growth % + FCF Margin %
4. **CAC Payback** = S&M / (Net New ARR × Gross Margin) × 12 months
5. **Implied runway** = Cash / Monthly Burn
6. **Hype Ratio** = ARR Growth Rate / Burn Multiple (higher is better)

How does this compare to [stage-appropriate] benchmarks?
```

## 3. Headcount Modeling

```
I need a headcount model for [company name] planning to grow from [X] to [Y] employees.

Current state:
- Headcount: [X] employees
- ARR: $[X]M
- ARR per employee: $[X]K
- Department mix: Engineering [X]%, Sales [X]%, Marketing [X]%, CS [X]%, G&A [X]%

Growth assumptions:
- Target ARR: $[X]M (in [X] months)
- Hiring plan by department: [provide or ask me to model]
- Average fully loaded cost: Engineering $[X]K, Sales $[X]K (OTE), Other $[X]K

Build:
1. **Monthly headcount ramp** by department with start dates
2. **Fully loaded cost model** (salary + benefits load [X]% + equity)
3. **Quota-carrying rep capacity model**: [X] reps × $[X]K quota × [X]% attainment
4. **ARR per employee trajectory** — does it improve or degrade with growth?
5. **Hiring vs. revenue timing**: Cash impact of hiring ahead of revenue
```

---

See also: `/budget`, `/forecast`, `/board-deck`
