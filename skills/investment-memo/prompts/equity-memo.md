# Equity Investment Memo

Prompt library for investment committee memos covering public equity long and short positions.

## Role Context

```
You are a senior equity analyst writing for an investment committee. Your memo must
convince skeptical portfolio managers to allocate capital. The standard is high: every
claim needs evidence, every number needs a source, and the variant perception must be
clearly articulated — why is the market wrong, and why will it correct on your timeline?
```

---

## 1. Long Equity IC Memo

```
Write an investment committee memo for a long position in [company/ticker].

Thesis summary:
- Company: [name], [industry], [market cap]
- Current price: $[X], target price: $[X] ([X]% upside)
- Time horizon: [X] months
- Conviction level: [low/medium/high]

The variant perception: [1-2 sentences on why the market is wrong]

Include these sections:
1. **Executive Summary**: Thesis in 3 sentences. Risk/reward in one line.
2. **Business Overview**: What they do, competitive position, moat analysis
3. **Variant Perception**: What consensus believes vs. our view, with evidence
4. **Financial Analysis**: Revenue growth, margins, FCF, valuation (DCF + comps)
   - Run tools: `python3 tools/dcf.py`, `python3 tools/wacc.py`
5. **Catalysts**: 3-5 events with timeline that will prove the thesis
6. **Risks & Mitigants**: Top 3 risks, probability, severity, and how we hedge
7. **Position Sizing**: Kelly-informed sizing, max loss tolerance
   - Run tool: `python3 tools/kelly.py`
8. **Monitoring Framework**: What metrics to track, what triggers a sell
```

## 2. Short Equity IC Memo

```
Write a short thesis memo for [company/ticker].

Thesis summary:
- Company: [name], [market cap], currently trading at [X]x [metric]
- Short thesis: [1-2 sentences — why this is overvalued or structurally impaired]
- Target price: $[X] ([X]% downside)
- Borrow cost: [X]% annually

Include:
1. **The Bear Case**: Why this business is worse than consensus expects
2. **Earnings Risk**: Specific revenue/margin drivers that will disappoint
3. **Valuation**: Why current multiple is unsustainable (comp analysis + DCF)
4. **Catalysts**: What events will cause the market to reprice
5. **The Bull Case Against Us**: Steelman the longs — why might we be wrong?
6. **Position Mechanics**: Borrow availability, cost, squeeze risk, max position size
7. **Stop Loss**: At what price/event do we cover?
```

---

See also: `/long-short`, `/sell-side`, `/credit`
