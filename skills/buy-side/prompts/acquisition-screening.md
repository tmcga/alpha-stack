# Acquisition Screening

Prompt library for buy-side M&A target identification, screening criteria, and preliminary evaluation.

## Role Context

```
You are a corporate development analyst evaluating acquisition targets. Your job is
to filter a universe of potential targets down to the 3-5 that deserve deep diligence.
You think in terms of strategic fit first, financial accretion second. The best
acquisition is the one where 1+1=3 — where the combined entity is worth more than
the sum of its parts for defensible, quantifiable reasons.
```

---

## 1. Target Screening Framework

```
Build an acquisition screening framework for [acquirer name] in [industry].

Strategic mandate: [describe what the acquirer wants — revenue growth, capability,
geographic expansion, technology, customer base, talent]

Acquirer profile:
- Revenue: $[X]M, growing [X]%
- EBITDA: $[X]M ([X]% margin)
- Market cap / EV: $[X]B
- Cash available: $[X]M
- Leverage capacity: [X]x EBITDA incremental debt

Screening criteria:
1. **Must-haves**: [industry fit, size range, geography, profitability threshold]
2. **Nice-to-haves**: [technology overlap, customer overlap, management team]
3. **Disqualifiers**: [regulatory risk, cultural mismatch, integration complexity]

For each target identified:
- Company description (2-3 sentences)
- Estimated revenue and growth rate
- Strategic rationale (why this target specifically)
- Estimated valuation range (using comparable transactions)
- Key risks and integration considerations
- Preliminary synergy estimate ($M, by type: revenue, cost, financial)
```

## 2. Synergy Analysis

```
Build a synergy model for [acquirer] acquiring [target].

Target financials:
- Revenue: $[X]M
- EBITDA: $[X]M ([X]% margin)
- Headcount: [X] employees

Synergy categories:
| Category | Description | Year 1 | Year 2 | Year 3 | Confidence |
|----------|-----------|--------|--------|--------|-----------|
| Cost: Headcount | [overlapping functions] | $[X]M | $[X]M | $[X]M | [H/M/L] |
| Cost: Facilities | [consolidation] | $[X]M | $[X]M | $[X]M | [H/M/L] |
| Cost: Technology | [platform consolidation] | $[X]M | $[X]M | $[X]M | [H/M/L] |
| Revenue: Cross-sell | [acquirer products → target customers] | $[X]M | $[X]M | $[X]M | [H/M/L] |
| Revenue: New market | [target products → acquirer channels] | $[X]M | $[X]M | $[X]M | [H/M/L] |

One-time integration costs:
- Severance: $[X]M
- Systems integration: $[X]M
- Retention bonuses: $[X]M
- Other: $[X]M

Calculate:
1. **Net present value of synergies** (discounted at [X]%)
2. **Synergy-adjusted valuation**: What can we afford to pay and still create value?
3. **Breakeven synergy**: Minimum synergies needed to justify the premium
4. **Integration risk**: What % of announced synergies are typically achieved in [industry]?
```

---

See also: `/sell-side`, `/lbo`, `/investment-memo`
