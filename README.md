# Alpha Stack

[![CI](https://github.com/tmcga/alpha-stack/actions/workflows/ci.yml/badge.svg)](https://github.com/tmcga/alpha-stack/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![Skills](https://img.shields.io/badge/skills-47-orange)
![Tools](https://img.shields.io/badge/tools-26-purple)

> What if every analyst had a senior MD's frameworks, a quant's toolkit, and a risk officer's discipline — loaded into their terminal and their spreadsheet?

**Alpha Stack** is an installable AI skill system for finance. 47 skills, 26 computational tools, a Bloomberg-inspired terminal, an Excel add-in with model templates, and a personal knowledge base that compounds over time.

### Why Alpha Stack?

- **Not prompts — pipelines.** Each skill is a 200-870 line execution pipeline with phased workflows, decision gates, and quality checks. Not a list of questions to ask.
- **Real math, not vibes.** 26 Python tools that run DCF, Black-Scholes, Monte Carlo, Black-Litterman, LBO, DSCR sizing, equity waterfalls, and more. Every recommendation is backed by a calculation you can verify.
- **Works where you work.** Bloomberg-style terminal (TUI), Excel sidebar with model templates, Claude Code skills, Claude Desktop MCP tools. Pick your interface.
- **Gets smarter over time.** Personal wiki tracks every company, thesis, and methodology preference. The Idea Map surfaces thesis drift, research gaps, and actionable signals.
- **Zero dependencies.** All core tools are stdlib-only Python. Install in 30 seconds. No API keys, no accounts, no subscriptions.

---

## Install (30 seconds)

```bash
git clone https://github.com/tmcga/alpha-stack.git ~/alpha-stack
cd ~/alpha-stack && ./setup.sh
```

Open Claude Code. Type `/sell-side`. You're running.

**For Claude Desktop** (no terminal needed): run `./setup-mcp.sh` instead. See [MCP Server](#claude-desktop-mcp-server) below.

---

## The Workflow

Every analysis follows six phases:

```
  Source ──> Diligence ──> Model ──> Stress ──> Decide ──> Monitor
    │           │            │          │          │          │
  Frame the   Research    Run the    Break the   Ship the   Track the
  question    deeply      numbers    thesis      memo       position
```

**Source** — Identify the opportunity. Frame the analytical question.
**Diligence** — Deep research using desk-specific prompt frameworks.
**Model** — Build the quantitative case. Run Python tools, sensitivity tables.
**Stress** — Pre-mortem. What kills this thesis? Who is on the other side?
**Decide** — Recommendation with conviction level, sizing, and risk/reward.
**Monitor** — Catalyst calendar, thesis-drift triggers, exit criteria.

---

## 47 Skills

**Deal & Banking**
| Command | What It Does |
|---------|-------------|
| `/sell-side` | Sell-side M&A — teaser, CIM, buyer mapping, bid evaluation, fairness opinion |
| `/buy-side` | Buy-side acquisition — target screening, valuation, synergies, offer structuring |
| `/lbo` | LBO modeling — debt sizing, returns attribution, sensitivity, exit analysis |
| `/restructuring` | Distressed — liquidity triage, waterfall, fulcrum security, plan of reorg |
| `/ipo` | IPO analysis — readiness, valuation, bookbuilding, pricing, stabilization |
| `/pitch-deck` | Pitch deck builder — startup fundraise, deal marketing, fund pitch, internal |
| `/investment-memo` | IC memo — equity L/S, PE/VC, credit, and real estate modes |

**Trading & Derivatives**
| Command | What It Does |
|---------|-------------|
| `/trade` | Execution analysis — block trades, VWAP/TWAP, market impact, TCA |
| `/derivatives` | Options pricing — Greeks, implied vol, strategy construction, convertibles |
| `/market-making` | Avellaneda-Stoikov — optimal quoting, inventory management, regime adaptation |

**Hedge Funds**
| Command | What It Does |
|---------|-------------|
| `/long-short` | L/S equity — variant perception, catalyst mapping, Kelly sizing, monitoring |
| `/macro` | Global macro — regime identification, cross-asset expression, geopolitical risk |
| `/merger-arb` | Event-driven — deal spread, implied probability, collar/CVR, portfolio exposure |
| `/credit` | Credit analysis — Z-Score, Merton model, recovery, relative value, IG/HY/distressed |

**Equity Research**
| Command | What It Does |
|---------|-------------|
| `/equity-research` | Initiating coverage — earnings models, trading comps, DCF, SOTP, price targets |
| `/earnings` | Earnings analysis — preview, post-earnings, estimate revisions, guidance tracking |

**Portfolio & Risk**
| Command | What It Does |
|---------|-------------|
| `/portfolio` | Portfolio construction — Black-Litterman, risk parity, factor, constrained optimization |
| `/risk` | Risk analytics — VaR/CVaR, Monte Carlo stress testing, factor decomposition, tail risk |
| `/attribution` | Performance attribution — Brinson-Fachler, factor, currency, fixed income, multi-period |

**Real Estate**
| Command | What It Does |
|---------|-------------|
| `/re-acquisitions` | Property acquisition underwriting — core, value-add, opportunistic strategies |
| `/re-development` | Ground-up development — cost build, lease-up, yield on cost, construction financing |
| `/re-debt` | Capital stack structuring — DSCR/LTV/debt yield sizing, mezzanine, preferred, bridge |
| `/re-reit` | Public REIT analysis — NAV, FFO/AFFO, implied cap rates, sector comps |

**Private Capital**
| Command | What It Does |
|---------|-------------|
| `/pe-buyout` | Control buyouts — LBO, platform + bolt-on, returns attribution, value creation |
| `/pe-growth` | Growth equity — minority stakes, unit economics, path to profitability, governance |
| `/private-credit` | Direct lending — unitranche, mezzanine, covenant design, risk-adjusted yield |
| `/secondaries` | LP secondaries — GP-led continuation, NAV lending, fund restructuring |

**Venture Capital**
| Command | What It Does |
|---------|-------------|
| `/vc-early` | Pre-seed through Series A — term sheets, SAFEs, cap tables, dilution modeling |
| `/vc-growth` | Series B+ — growth metrics, biotech rNPV, crypto token economics, secondary shares |
| `/vc-fund` | Fund construction — portfolio math, reserves, power law, J-curve, LP reporting |

**Wealth Management**
| Command | What It Does |
|---------|-------------|
| `/retirement` | Retirement planning — Monte Carlo, withdrawal strategy, Social Security, Roth conversion |
| `/estate` | Estate & tax planning — trusts, GRATs, gifting, dynasty trusts, family office |
| `/insurance` | Insurance analysis — life, disability, LTC, annuities, key person, buy-sell |

**Quant**
| Command | What It Does |
|---------|-------------|
| `/quant` | Strategy development — signals, backtesting, overfitting detection, LLM sentiment, regime |

**CFO & Corporate Finance**
| Command | What It Does |
|---------|-------------|
| `/budget` | Annual budget build, variance analysis, zero-based budgeting, departmental review |
| `/forecast` | Rolling forecasts, 13-week cash flow, scenario planning, revenue modeling |
| `/board-deck` | Board reporting, KPI dashboards, investor updates, earnings prep |
| `/fpa` | FP&A — unit economics, SaaS metrics, headcount modeling, strategic finance |

**Accounting & Data**
| Command | What It Does |
|---------|-------------|
| `/accounting` | Journal entries, accruals, closing process, chart of accounts, ASC 606/842 |
| `/financial-statements` | P&L, balance sheet, cash flow (indirect method), ratio analysis, DuPont |
| `/audit` | Audit planning, risk assessment, substantive testing, controls, sampling |
| `/data-entry` | Financial data extraction, cleaning, normalization, validation |

**Knowledge Base**
| Command | What It Does |
|---------|-------------|
| `/wiki` | Personal knowledge base — ingest analyses, query prior research, track methodology preferences. Compounds over time. |

Each skill is an execution pipeline with phased workflows, decision gates, tool integration, quality gates, hard constraints, and common pitfalls.

Every skill has a **ready-to-paste example** in [`examples/`](examples/) — realistic scenarios with all inputs pre-filled so you can try any skill immediately without inventing data.

---

## 26 Computational Tools

Standalone Python calculators. Zero dependencies — just Python 3.10+. Run from CLI or import as modules.

| Domain | Tools |
|--------|-------|
| **Valuation** | `dcf.py` `lbo.py` `wacc.py` `irr.py` |
| **Options** | `black_scholes.py` `implied_vol.py` `convertible.py` |
| **Fixed Income & Credit** | `bond_yield.py` `merton_model.py` `credit_spread.py` |
| **Portfolio & Risk** | `portfolio_risk.py` `kelly.py` `brinson.py` `black_litterman.py` `monte_carlo.py` |
| **M&A** | `merger_arb.py` |
| **Real Estate** | `cap_rate.py` `re_debt.py` `re_waterfall.py` `re_development.py` `re_noi.py` |
| **VC / Lending** | `vc_returns.py` `loan_amort.py` |
| **Tax & Depreciation** | `depreciation.py` |
| **Quant Trading** | `market_maker.py` |
| **Knowledge Base** | `wiki.py` |

```bash
# Run any tool directly
python3 tools/dcf.py --fcf 100,110,121,133,146 --wacc 0.10 --terminal-growth 0.025 --shares 100
python3 tools/re_debt.py --noi 1800000 --value 28000000 --rate 0.0625 --min-dscr 1.25 --max-ltv 0.65
python3 tools/re_waterfall.py --equity 10000000 --cfs 800000,900000,1000000,1100000,15000000
python3 tools/irr.py --cfs="-1000000,200000,300000,400000,500000"
```

Full tool documentation at [tools/README.md](tools/README.md).

---

## Personal Knowledge Base (`/wiki`)

Alpha Stack gets smarter the longer you use it. The `/wiki` skill builds a personal finance knowledge base — a persistent, local collection of markdown files that captures every company you research, every thesis you form, and every methodology preference you express.

Inspired by Karpathy's [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) pattern.

```
You:    /wiki init
Claude: Wiki initialized at ~/.alpha-stack/wiki/

You:    /wiki — ingest my AAPL analysis: services mix shifting from 22% to 35%,
        driving P/E expansion from 28x to 32x. Target $245. Key risk: EU antitrust.
Claude: Created entities/aapl.md, journal/aapl-services-thesis-2026-04-05.md
        Updated index.md with cross-references.

        --- 3 months later ---

You:    What do I know about Apple?
Claude: Per your analysis from 2026-04-05 (journal/aapl-services-thesis-2026-04-05.md):
        Thesis: services mix shift → P/E expansion to 32x. Target $245.
        Key risk: EU antitrust forcing App Store fee reductions.
```

**How it works:**
- **Entities** — company/sector pages that accumulate across analyses
- **Journal** — dated analysis records with thesis, findings, recommendation, and outcome tracking
- **Playbooks** — your preferred methodologies ("I use 10% WACC for mid-cap tech")
- **Schema** — conventions that evolve as the LLM learns your style

Everything stays local at `~/.alpha-stack/wiki/`. Nothing is committed to the repo. The wiki is yours — just markdown files you can browse, git-track separately, or back up however you want.

---

## Bloomberg Terminal (TUI)

A full terminal interface with live market data, inspired by the Bloomberg Terminal.

```bash
./setup-tui.sh && python -m tui
```

**4 screens, keyboard-driven (F1-F4):**

| Screen | Key | What It Shows |
|--------|-----|--------------|
| **Dashboard** | F1 | Live market indices (S&P, Dow, Nasdaq, VIX), treasury yield curve, wiki status, recent sessions |
| **Wiki Browser** | F2 | Browse entities/playbooks/journal with tree nav + markdown viewer + search |
| **Tool Runner** | F3 | Run any of 25 tools with dynamic parameter forms, formatted results, save to session |
| **Idea Map** | F4 | Intelligence layer — surfaces thesis drift, outcome tracking, research gaps, risk monitors from your wiki |

The Idea Map is what makes the wiki compound — it mines your knowledge base and cross-references with live market data to tell you what needs attention: "AAPL is +18% past your $245 target", "CyberVault LBO thesis is 90 days old with Open outcome", "Your DCF playbook hasn't been updated in 6 months."

Dark navy/amber theme. Live yfinance data. All data stays local.

---

## Excel Add-in

Alpha Stack inside Excel — for bankers, PE associates, CFOs, and real estate professionals who live in spreadsheets.

```bash
./plugin/setup-excel.sh
# In Excel: Insert → Get Add-ins → Upload manifest.xml
```

**6 sidebar tabs:**

| Tab | What It Does |
|-----|-------------|
| **Tools** | Pick any of 25 tools, fill dynamic forms, run, write results to cells with banker formatting |
| **Sensitivity** | Select output + two params → generates 5x5 sensitivity grid with conditional formatting |
| **Scenarios** | Define Base/Bull/Bear, toggle assumptions, compare side-by-side |
| **Templates** | 9 model templates with yellow input cells — LBO, DCF, Merger, Debt Sizing, Waterfall, Cap Table, Portfolio, Retirement, Operating |
| **Audit** | Scan for hardcoded values, broken refs, formula errors, sign convention issues |
| **Library** | Version snapshots with diff, saved sessions, wiki search |

**Model templates generate multi-tab workbooks** with banker-grade formatting: yellow-shaded inputs, blue hardcoded values, gray labels, proper number formats ($X.XM, X.X%, X.Xx), and borders. They match the formatting conventions of every major bank and PE shop.

---

## Claude Desktop (MCP Server)

Alpha Stack is also a **finance MCP server** — 45 tools that Claude Desktop can call natively. No terminal, no Python knowledge. Just ask a question and Claude runs the math.

### Setup

```bash
git clone https://github.com/tmcga/alpha-stack.git ~/alpha-stack
cd ~/alpha-stack && ./setup-mcp.sh
```

Restart Claude Desktop. Look for the hammer icon — that means the tools are live.

<details>
<summary>Manual setup (without installer)</summary>

1. Install [uv](https://docs.astral.sh/uv/): `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. Install dependencies: `cd ~/alpha-stack && uv sync`
3. Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "alpha-stack": {
      "command": "uv",
      "args": ["run", "--directory", "/absolute/path/to/alpha-stack", "python", "mcp_server.py"]
    }
  }
}
```
4. Restart Claude Desktop.
</details>

### What It Looks Like

```
You:    I'm looking at a company with EBITDA of $100M. Entry at 10x, exit at 11x,
        5x leverage, 6% rate, 8% EBITDA growth, 5 year hold. What are sponsor returns?

Claude: [calls lbo_returns tool]

        MOIC: 2.99x
        IRR: 24.5%

        Returns Attribution:
          EBITDA Growth:    0.9%
          Multiple Change: 27.6%
          Deleveraging:    71.5%
```

```
You:    Size a senior loan on a $28M property with $1.8M NOI at 6.25%.

Claude: [calls re_debt_sizing tool]

        Binding Constraint: LTV
        Max Loan:     $18,200,000
        Actual DSCR:  1.34x
        Debt Yield:   9.89%
        Positive Leverage: YES
```

---

## See It In Action

Full annotated example outputs with real tool results:

- **[Sell-Side M&A](examples/outputs/sell-side-chemicals.md)** — DCF valuation, LBO floor, buyer universe, risk matrix for a specialty chemical company
- **[LBO Analysis](examples/outputs/lbo-software-buyout.md)** — Returns attribution, sensitivity tables, debt schedule for a cloud security buyout
- **[Long/Short Equity](examples/outputs/long-short-semis.md)** — Variant perception thesis, Kelly sizing, catalyst calendar for semi equipment
- **[Retirement Planning](examples/outputs/retirement-monte-carlo.md)** — Monte Carlo simulation, ruin probability, portfolio recommendations
- **[Performance Attribution](examples/outputs/quarterly-attribution.md)** — Brinson-Fachler decomposition, CIO commentary

Every skill also has a **ready-to-paste example scenario** in [`examples/`](examples/) — try any skill immediately without inventing data.

---

## Philosophy

Alpha Stack is built on seven principles documented in [ETHOS.md](ETHOS.md):

1. **Assumptions are the model** — every number is a bet; make the bets explicit
2. **Second-order thinking** — "and then what?" is the most important question
3. **Adversarial by default** — pre-mortem every thesis before it gets capital
4. **Precision over confidence** — ranges over point estimates, distributions over averages
5. **Tools verify intuition** — run the math, then interpret
6. **Cross-desk fluency** — seeing all perspectives is the edge
7. **No hallucinated numbers** — if the data doesn't exist, ask for it

---

## Project Structure

```
alpha-stack/
├── CLAUDE.md              AI-native instructions for Claude Code
├── ETHOS.md               The Alpha Edge — finance AI philosophy
├── setup.sh               Claude Code skill installer (30 seconds)
├── setup-mcp.sh           Claude Desktop MCP installer
├── setup-tui.sh           Bloomberg Terminal TUI installer
├── mcp_server.py          MCP server (45 tools for Claude Desktop)
├── pyproject.toml         Python dependencies
├─��� skills/                47 skill directories (SKILL.md + prompts/)
├── tools/                 26 Python calculators (stdlib-only)
├── tui/                   Bloomberg Terminal TUI (Textual)
│   ├── app.py             Main app — F1-F4 screen routing
│   ├── bloomberg.tcss     Dark navy/amber theme
│   ├── ideas.py           Idea engine — mines wiki for actionable signals
│   ├── data.py            Live market data via yfinance
│   ├── registry.py        25 tools with full parameter metadata
│   ├── screens/           Dashboard, Wiki Browser, Tool Runner, Idea Map
│   └── widgets/           Command bar, ticker bar, forms, result panel
├── plugin/                Excel Office Add-in
│   ├── server/            FastAPI server wrapping all tools as REST endpoints
│   │   ├── app.py         API server with CORS + static file serving
│   │   ├── templates.py   9 model template definitions
│   │   └── output_mapper.py  Tool results → Excel cell layouts
│   ├── addin/             Sidebar UI (HTML/CSS/JS + Office.js)
│   │   ├── manifest.xml   Office Add-in manifest for sideloading
│   │   ├── taskpane.html  6-tab sidebar (Tools, Sens, Scenarios, Templates, Audit, Library)
│   │   ├── taskpane.css   Professional banker-grade theme
│   │   └── taskpane.js    Client logic — forms, API calls, cell writes
│   └── setup-excel.sh     One-script installer
├── examples/              26 ready-to-paste scenarios + 5 annotated outputs
├── tests/                 113 pytest tests
└── docs/                  Workflow documentation
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding new skills, prompts, or tools. Scaffolding scripts in [`scripts/`](scripts/) create properly structured files from templates. All contributions welcome.

## License

[MIT](LICENSE) — use it however you want.
