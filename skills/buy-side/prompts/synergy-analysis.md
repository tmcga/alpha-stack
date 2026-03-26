# Due Diligence & Offer Structuring

Prompt library for buy-side due diligence frameworks and offer structuring.

## Role Context

```
You are a VP of corporate development structuring an acquisition offer. You balance
the need to win the deal against the discipline to not overpay. Every dollar of
premium must be justified by synergies, strategic value, or scarcity — and the
justification must survive a board presentation.
```

---

## 1. Due Diligence Checklist

```
Build a due diligence framework for [acquirer] evaluating [target] in [industry].

Deal stage: [LOI signed / exclusivity / pre-offer]
Expected timeline: [X] weeks

Priority diligence areas:
1. **Financial**: Quality of earnings, revenue sustainability, working capital normalization
   - Adjusted EBITDA: What addbacks are defensible?
   - Customer concentration: Top 10 customers as % of revenue
   - Revenue quality: Recurring vs. one-time, contract terms, renewal rates

2. **Commercial**: Market position, competitive dynamics, customer references
   - Win/loss analysis: Why do customers choose (or leave) this company?
   - Pipeline quality: Is the sales forecast achievable?

3. **Technology / IP**: Product architecture, tech debt, IP ownership
   - Build vs. buy analysis: Could we replicate this for less?
   - Integration complexity: How hard is it to merge platforms?

4. **People & Culture**: Key person risk, retention planning, cultural fit
   - Who are the 10 people we cannot afford to lose?
   - Compensation benchmarking: Are we buying expensive talent?

5. **Legal & Regulatory**: Contracts, litigation, compliance, antitrust
   - Change of control provisions in key contracts
   - Regulatory approval timeline and risk

For each area: Flag items as [green/yellow/red] with action items for resolution.
```

## 2. Offer Structuring

```
Structure an acquisition offer for [target] by [acquirer].

Valuation range:
- DCF value: $[X-Y]M
- Comparable transactions: [X-Y]x EBITDA = $[X-Y]M
- Strategic value (with synergies): $[X-Y]M
- Run tools: `python3 tools/dcf.py`, `python3 tools/lbo.py`

Structuring considerations:
- Acquirer stock price: $[X] (premium/discount to NAV?)
- Target preference: [cash/stock/mixed]
- Tax implications: [stock-for-stock tax-free reorganization possible?]
- Financing: Cash on hand $[X]M, debt capacity $[X]M, stock issuance capacity

Build offer scenarios:
1. **All-cash offer** at $[X]M — financing plan and EPS impact
2. **Mixed offer** ([X]% cash / [X]% stock) — accretion/dilution analysis
3. **Stock-for-stock** at [exchange ratio] — premium and ownership split
4. **Earnout structure** — $[X]M upfront + $[X]M contingent on [milestones]

For each scenario: EPS accretion/dilution in Year 1 and Year 2, pro forma leverage, and ROIC vs. WACC.
```

---

See also: `/sell-side`, `/lbo`, `/merger-arb`
