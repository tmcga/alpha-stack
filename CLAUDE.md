# Alpha Stack

This is **Alpha Stack** — an installable AI skill system for finance. 12 skills, 19 computational tools, and a structured workflow for investment analysis.

## Skill Registry

| Command | Skill | What It Does |
|---------|-------|-------------|
| `/deal` | deal-execution | M&A advisory, leveraged finance, restructuring |
| `/markets` | capital-markets | ECM, DCM, equity research |
| `/derivatives` | options-and-derivatives | Options pricing, structured products |
| `/trade` | trading-and-execution | Cash equities, fixed income, FX, commodities, market making |
| `/hedge` | hedge-fund-strategies | L/S equity, macro, quant, event-driven, credit |
| `/pe` | private-capital | Buyouts, growth equity, special situations, private credit |
| `/real-assets` | real-assets | Real estate, infrastructure |
| `/portfolio` | portfolio-construction | Active equity, factor, multi-asset, alternatives allocation |
| `/risk` | risk-analytics | Portfolio risk, VaR/CVaR, stress testing |
| `/vc` | venture-capital | Early/growth stage, biotech, crypto, platform ops |
| `/wealth` | wealth-advisory | Private banking, financial planning, estate/tax |
| `/quant` | quant-signals | Strategy development, LLM sentiment, cross-desk analysis |

## The Alpha Stack Workflow

Every analysis follows six phases: **Source > Diligence > Model > Stress > Decide > Monitor**

1. **Source** — Identify the opportunity. Gather context, frame the question.
2. **Diligence** — Deep research using skill prompts. Structured analysis, cross-desk perspectives.
3. **Model** — Build the quantitative framework. Run Python tools, construct sensitivity tables.
4. **Stress** — Challenge every assumption. Pre-mortem, tail risk, Monte Carlo scenarios.
5. **Decide** — Synthesize into a recommendation with explicit risk/reward and conviction level.
6. **Monitor** — Define tracking criteria: thesis drift, catalysts, exit triggers, rebalancing rules.

## Tool Invocation

When a user's question involves quantitative analysis, run the relevant Python tool and show the output. Tools are in `tools/` and require only Python 3.10+ (no external dependencies).

| When the user asks about... | Run this tool |
|----------------------------|---------------|
| Company valuation, DCF, intrinsic value | `python3 tools/dcf.py` |
| LBO, leveraged buyout, PE returns | `python3 tools/lbo.py` |
| Cost of capital, WACC | `python3 tools/wacc.py` |
| Options pricing, Greeks, Black-Scholes | `python3 tools/black_scholes.py` |
| Implied volatility from option prices | `python3 tools/implied_vol.py` |
| Convertible bonds | `python3 tools/convertible.py` |
| Bond yield, duration, DV01 | `python3 tools/bond_yield.py` |
| Default risk, credit model | `python3 tools/merton_model.py` |
| Z-Score, CDS spread, credit analysis | `python3 tools/credit_spread.py` |
| Portfolio risk, Sharpe, drawdown, VaR | `python3 tools/portfolio_risk.py` |
| Position sizing, Kelly criterion | `python3 tools/kelly.py` |
| Performance attribution, Brinson | `python3 tools/brinson.py` |
| Portfolio optimization, Black-Litterman | `python3 tools/black_litterman.py` |
| Monte Carlo simulation, retirement | `python3 tools/monte_carlo.py` |
| Merger arb spread, deal probability | `python3 tools/merger_arb.py` |
| Real estate, cap rate, NOI | `python3 tools/cap_rate.py` |
| VC fund returns, dilution, TVPI | `python3 tools/vc_returns.py` |
| Loan amortization, mortgage | `python3 tools/loan_amort.py` |
| Market making, optimal quoting | `python3 tools/market_maker.py` |

## Output Standards

When producing financial analysis:

- **Assumptions first.** Every number is a bet. List assumptions explicitly before presenting results.
- **Ranges over points.** Never present a single-point estimate without a sensitivity table or confidence range.
- **Show your work.** Include the tool command and its output so the user can verify and re-run with different inputs.
- **Risk caveats.** Every recommendation must include what kills the thesis — the bear case, the tail risk, the regime change.
- **No hallucinated numbers.** If the user has not provided a data point, ask for it. Never fabricate financial data.

## Cross-Desk Analysis

When analyzing a company, event, or market move, offer to show it through multiple desk perspectives. The same acquisition looks different to an M&A banker, an event-driven hedge fund, a credit analyst, and an equity research analyst. Cross-referencing is a first-class feature — it is often where the real edge is found.

## Repo Structure

```
skills/          12 skill directories, each with SKILL.md + prompts/
tools/           19 standalone Python calculators (stdlib-only, <200 lines each)
mcp_server.py    MCP server exposing all tools for Claude Desktop
docs/            Workflow documentation
ETHOS.md         Finance AI philosophy
```
