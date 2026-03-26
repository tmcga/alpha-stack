# Cash Flow Forecasting

Prompt library for cash flow modeling, 13-week projections, and liquidity management.

## Role Context

```
You are a treasury analyst who knows that cash flow is the only number that can't
be manipulated by accounting choices. Revenue is an opinion. Cash is a fact. Your
forecasts must be precise at the weekly level and conservative by default — running
out of cash is an existential event, not a rounding error.
```

---

## 1. 13-Week Cash Flow

```
Build a 13-week cash flow forecast for [company name].

Starting position:
- Cash on hand: $[X]M
- Revolver availability: $[X]M
- Minimum operating cash: $[X]M

Weekly cash flow drivers:
| Category | Weekly Avg | Variability | Notes |
|----------|-----------|-------------|-------|
| Collections (recurring) | $[X]K | [Low/Med/High] | [billing terms] |
| Collections (one-time) | $[X]K | [Low/Med/High] | [deal timing] |
| Payroll | -$[X]K | Low | [cycle: weekly/biweekly] |
| Rent & facilities | -$[X]K | None | Fixed |
| Vendor payments | -$[X]K | Medium | [payment terms] |
| Debt service | -$[X]K | None | [loan details] |
| Capex | -$[X]K | [Low/Med/High] | [if applicable] |

Known events in the 13-week window:
- Week [X]: [describe event and amount]
- Week [X]: [describe event and amount]

Build:
1. **Week-by-week projection** with running cash balance
2. **Minimum cash date**: When does balance hit the floor?
3. **Sensitivity**: What if collections slip by [1/2] weeks?
4. **Scenario overlay**: Best case, base case, stress case
5. **Decision triggers**: At what cash level do we [draw revolver / cut spend / raise capital]?
```

## 2. Working Capital Optimization

```
Analyze working capital for [company name]:

Current metrics:
- Days Sales Outstanding (DSO): [X] days
- Days Inventory Outstanding (DIO): [X] days (if applicable)
- Days Payable Outstanding (DPO): [X] days
- Cash Conversion Cycle: DSO + DIO - DPO = [X] days

Quarterly working capital:
| Quarter | Receivables | Inventory | Payables | Net WC |
|---------|------------|-----------|----------|--------|
| [Q-4] | $[X]M | $[X]M | $[X]M | $[X]M |
| [Q-3] | $[X]M | $[X]M | $[X]M | $[X]M |
| [Q-2] | $[X]M | $[X]M | $[X]M | $[X]M |
| [Q-1] | $[X]M | $[X]M | $[X]M | $[X]M |

Analyze:
1. **Trend**: Is the cash conversion cycle improving or deteriorating?
2. **Cash impact**: Every 1-day improvement in DSO frees $[X]K
3. **Levers**: Rank opportunities by cash impact and feasibility
4. **Benchmark**: How does our CCC compare to [industry] peers?
```

---

See also: `/budget`, `/fpa`, `/restructuring`
