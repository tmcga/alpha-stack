# Credit Investment Memo

Prompt library for credit investment committee memos covering IG, HY, and distressed debt.

## Role Context

```
You are a credit analyst writing for a fixed income investment committee. You think
in terms of downside protection first — the upside in credit is capped (you get your
coupons and par), but the downside is losing principal. Your analysis focuses on
ability to pay, willingness to pay, and recovery in default scenarios.
```

---

## 1. High Yield Credit Memo

```
Write a credit investment memo for [issuer name] [bond description].

Bond details:
- Issuer: [name], [industry]
- Bond: [coupon]% [seniority] due [maturity]
- Current price: $[X] (yield: [X]%, spread: +[X]bps)
- Rating: [Moody's]/[S&P]
- Outstanding: $[X]M

Issuer financials:
- Revenue: $[X]M, [trend]
- EBITDA: $[X]M ([X]% margin)
- Total leverage: [X]x
- Interest coverage: [X]x
- Free cash flow: $[X]M
- Liquidity: $[X]M cash + $[X]M revolver availability

Include:
1. **Credit Summary**: Investment grade, crossover, or distressed? Why?
2. **Capital Structure**: Full debt stack with amounts, rates, maturities, covenants
3. **Cash Flow Analysis**: Can the issuer service debt through maturity?
   - Run tools: `python3 tools/credit_spread.py`, `python3 tools/merton_model.py`
4. **Recovery Analysis**: In a default, what do we recover? Waterfall by tranche
5. **Relative Value**: Spread vs. rating-matched peers — cheap or expensive?
6. **Covenant Analysis**: Key covenants, headroom, and trigger risks
7. **Recommendation**: Buy/sell/hold with target spread and price
```

## 2. Distressed Debt Memo

```
Write a distressed debt analysis for [issuer name].

Current situation:
- Bond trading at $[X] (yield: [X]%)
- Why distressed: [describe — liquidity, covenant breach, operational decline]
- Key question: Restructuring or recovery?

Include:
1. **Liquidation analysis**: What is the business worth in pieces?
2. **Going-concern analysis**: What is the business worth operating?
3. **Fulcrum security identification**: Which tranche owns the equity post-restructuring?
4. **Recovery matrix**: Scenarios with probability weights
5. **Catalyst timeline**: When does the situation resolve?
6. **Risk of permanent impairment** vs. temporary dislocation
```

---

See also: `/credit`, `/restructuring`, `/long-short`
