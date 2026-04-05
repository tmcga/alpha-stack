"""Tool metadata registry — drives the TUI's dynamic form builder and tool tree."""

import importlib

# Parameter type shorthands
F = "float"
I = "int"
S = "str"
LF = "list[float]"
LLF = "list[list[float]]"

CATEGORIES = [
    "Valuation",
    "Options",
    "Fixed Income",
    "Portfolio",
    "M&A / Trading",
    "Real Estate",
    "VC / Lending",
]


def _p(name, typ, label, required=True, default=None, hint=""):
    return {"name": name, "type": typ, "label": label, "required": required, "default": default, "hint": hint}


TOOLS = {
    # ── Valuation ──
    "dcf": {
        "name": "DCF Valuation",
        "module": "dcf",
        "fn": "dcf_valuation",
        "category": "Valuation",
        "params": [
            _p("fcfs", LF, "Free Cash Flows", hint="100,110,121,133,146"),
            _p("wacc", F, "WACC", hint="0.10"),
            _p("terminal_growth", F, "Terminal Growth", required=False, hint="0.025"),
            _p("exit_multiple", F, "Exit Multiple", required=False, hint="12"),
            _p("net_debt", F, "Net Debt", required=False, default=0),
            _p("shares", F, "Shares", required=False, default=1),
        ],
    },
    "lbo": {
        "name": "LBO Returns",
        "module": "lbo",
        "fn": "lbo_returns",
        "category": "Valuation",
        "params": [
            _p("ebitda", F, "EBITDA"),
            _p("entry_multiple", F, "Entry Multiple", hint="10"),
            _p("exit_multiple", F, "Exit Multiple", hint="11"),
            _p("leverage", F, "Leverage (x EBITDA)", hint="5"),
            _p("interest_rate", F, "Interest Rate", hint="0.06"),
            _p("ebitda_growth", F, "EBITDA Growth", hint="0.08"),
            _p("years", I, "Hold Period (years)", hint="5"),
            _p("amortization_pct", F, "Amort %", required=False, default=0.01),
        ],
    },
    "wacc": {
        "name": "WACC",
        "module": "wacc",
        "fn": "wacc",
        "category": "Valuation",
        "params": [
            _p("equity_value", F, "Equity Value"),
            _p("debt_value", F, "Debt Value"),
            _p("tax_rate", F, "Tax Rate", hint="0.21"),
            _p("risk_free", F, "Risk-Free Rate"),
            _p("beta", F, "Beta"),
            _p("equity_risk_premium", F, "ERP", hint="0.055"),
            _p("cost_of_debt", F, "Cost of Debt"),
        ],
    },
    "irr": {
        "name": "IRR / NPV",
        "module": "irr",
        "fn": "irr_solve",
        "category": "Valuation",
        "params": [
            _p("cash_flows", LF, "Cash Flows", hint="-1000,200,300,400,500"),
        ],
    },
    # ── Options ──
    "black_scholes": {
        "name": "Black-Scholes",
        "module": "black_scholes",
        "fn": "black_scholes",
        "category": "Options",
        "params": [
            _p("spot", F, "Spot Price"),
            _p("strike", F, "Strike Price"),
            _p("time", F, "Time to Expiry (years)", hint="0.25"),
            _p("rate", F, "Risk-Free Rate"),
            _p("vol", F, "Volatility", hint="0.30"),
            _p("option_type", S, "Type (call/put)", required=False, default="call"),
        ],
    },
    "implied_vol": {
        "name": "Implied Volatility",
        "module": "implied_vol",
        "fn": "implied_volatility",
        "category": "Options",
        "params": [
            _p("market_price", F, "Market Price"),
            _p("spot", F, "Spot Price"),
            _p("strike", F, "Strike Price"),
            _p("time", F, "Time to Expiry"),
            _p("rate", F, "Risk-Free Rate"),
            _p("option_type", S, "Type (call/put)", required=False, default="call"),
        ],
    },
    "convertible": {
        "name": "Convertible Bond",
        "module": "convertible",
        "fn": "convertible_bond",
        "category": "Options",
        "params": [
            _p("face", F, "Face Value"),
            _p("coupon_rate", F, "Coupon Rate"),
            _p("maturity", F, "Maturity (years)"),
            _p("credit_spread", F, "Credit Spread"),
            _p("stock_price", F, "Stock Price"),
            _p("conversion_ratio", F, "Conversion Ratio"),
            _p("stock_vol", F, "Stock Volatility"),
            _p("risk_free", F, "Risk-Free Rate"),
        ],
    },
    # ── Fixed Income ──
    "bond_yield": {
        "name": "Bond Analytics",
        "module": "bond_yield",
        "fn": "bond_analytics",
        "category": "Fixed Income",
        "params": [
            _p("face", F, "Face Value", hint="1000"),
            _p("coupon_rate", F, "Coupon Rate", hint="0.05"),
            _p("price", F, "Market Price", hint="980"),
            _p("years", F, "Years to Maturity"),
            _p("freq", I, "Coupon Frequency", required=False, default=2),
        ],
    },
    "merton": {
        "name": "Merton Default Model",
        "module": "merton_model",
        "fn": "merton_model",
        "category": "Fixed Income",
        "params": [
            _p("asset_value", F, "Asset Value"),
            _p("debt_face", F, "Debt Face Value"),
            _p("asset_vol", F, "Asset Volatility"),
            _p("risk_free", F, "Risk-Free Rate"),
            _p("maturity", F, "Maturity"),
        ],
    },
    "zscore": {
        "name": "Altman Z-Score",
        "module": "credit_spread",
        "fn": "altman_zscore",
        "category": "Fixed Income",
        "params": [
            _p("wc_ta", F, "Working Capital / TA"),
            _p("re_ta", F, "Retained Earnings / TA"),
            _p("ebit_ta", F, "EBIT / TA"),
            _p("equity_debt", F, "Equity / Total Debt"),
            _p("sales_ta", F, "Sales / TA"),
        ],
    },
    # ── Portfolio ──
    "portfolio_risk": {
        "name": "Portfolio Risk",
        "module": "portfolio_risk",
        "fn": "portfolio_metrics",
        "category": "Portfolio",
        "params": [
            _p("returns", LF, "Returns (periods)", hint="0.01,-0.02,0.03,..."),
            _p("risk_free", F, "Risk-Free Rate", required=False, default=0.0),
            _p("periods_per_year", I, "Periods/Year", required=False, default=12),
        ],
    },
    "kelly": {
        "name": "Kelly Criterion",
        "module": "kelly",
        "fn": "kelly_criterion",
        "category": "Portfolio",
        "params": [
            _p("win_prob", F, "Win Probability", hint="0.55"),
            _p("win_loss_ratio", F, "Win/Loss Ratio", hint="1.5"),
            _p("fraction", F, "Kelly Fraction", required=False, default=1.0),
        ],
    },
    "brinson": {
        "name": "Brinson Attribution",
        "module": "brinson",
        "fn": "brinson_attribution",
        "category": "Portfolio",
        "params": [
            _p("port_weights", LF, "Portfolio Weights", hint="0.3,0.3,0.4"),
            _p("port_returns", LF, "Portfolio Returns", hint="0.12,0.05,0.08"),
            _p("bench_weights", LF, "Benchmark Weights", hint="0.33,0.33,0.34"),
            _p("bench_returns", LF, "Benchmark Returns", hint="0.10,0.06,0.07"),
        ],
    },
    "black_litterman": {
        "name": "Black-Litterman",
        "module": "black_litterman",
        "fn": "black_litterman",
        "category": "Portfolio",
        "params": [
            _p("market_weights", LF, "Market Weights", hint="0.6,0.4"),
            _p("cov_matrix", LLF, "Covariance Matrix", hint="[[0.04,0.01],[0.01,0.03]]"),
            _p("risk_aversion", F, "Risk Aversion", hint="2.5"),
            _p("tau", F, "Tau", hint="0.05"),
        ],
    },
    "monte_carlo": {
        "name": "Monte Carlo",
        "module": "monte_carlo",
        "fn": "monte_carlo_sim",
        "category": "Portfolio",
        "params": [
            _p("initial", F, "Initial Value", hint="1000000"),
            _p("expected_return", F, "Expected Return", hint="0.07"),
            _p("volatility", F, "Volatility", hint="0.15"),
            _p("years", I, "Years", hint="30"),
            _p("num_sims", I, "Simulations", required=False, default=10000),
            _p("withdrawal_rate", F, "Withdrawal Rate", required=False, default=0.0),
        ],
    },
    # ── M&A / Trading ──
    "merger_arb": {
        "name": "Merger Arb",
        "module": "merger_arb",
        "fn": "merger_arb",
        "category": "M&A / Trading",
        "params": [
            _p("current_price", F, "Current Price"),
            _p("offer_price", F, "Offer Price"),
            _p("days_to_close", I, "Days to Close"),
            _p("risk_free", F, "Risk-Free Rate", required=False, default=0.05),
            _p("downside_price", F, "Downside Price", required=False),
        ],
    },
    "market_maker": {
        "name": "Market Maker",
        "module": "market_maker",
        "fn": "optimal_quotes",
        "category": "M&A / Trading",
        "params": [
            _p("mid_price", F, "Mid Price"),
            _p("inventory", I, "Inventory"),
            _p("risk_aversion", F, "Risk Aversion", hint="0.01"),
            _p("volatility", F, "Volatility"),
            _p("time_remaining", F, "Time Remaining"),
            _p("order_intensity", F, "Order Intensity", hint="1.5"),
        ],
    },
    # ── Real Estate ──
    "cap_rate": {
        "name": "Cap Rate / NOI",
        "module": "cap_rate",
        "fn": "real_estate_valuation",
        "category": "Real Estate",
        "params": [
            _p("noi", F, "NOI"),
            _p("cap_rate", F, "Cap Rate", required=False, hint="0.05"),
            _p("property_value", F, "Property Value", required=False),
        ],
    },
    "re_debt": {
        "name": "RE Debt Sizing",
        "module": "re_debt",
        "fn": "debt_sizing",
        "category": "Real Estate",
        "params": [
            _p("noi", F, "NOI"),
            _p("property_value", F, "Property Value"),
            _p("rate", F, "Interest Rate"),
            _p("max_ltv", F, "Max LTV", required=False, default=0.75),
            _p("min_dscr", F, "Min DSCR", required=False, default=1.25),
        ],
    },
    "re_waterfall": {
        "name": "Equity Waterfall",
        "module": "re_waterfall",
        "fn": "equity_waterfall",
        "category": "Real Estate",
        "params": [
            _p("equity_invested", F, "Equity Invested"),
            _p("cash_flows", LF, "Cash Flows", hint="800000,900000,...,15000000"),
        ],
    },
    "re_dev": {
        "name": "Development Pro Forma",
        "module": "re_development",
        "fn": "development_proforma",
        "category": "Real Estate",
        "params": [
            _p("land_cost", F, "Land Cost"),
            _p("hard_costs", F, "Hard Costs"),
            _p("stabilized_noi", F, "Stabilized NOI", required=False, default=0),
            _p("exit_cap_rate", F, "Exit Cap Rate", required=False, default=0.055),
        ],
    },
    "re_noi": {
        "name": "NOI Builder",
        "module": "re_noi",
        "fn": "noi_builder",
        "category": "Real Estate",
        "params": [
            _p("units", I, "Units"),
            _p("avg_rent_monthly", F, "Avg Monthly Rent"),
            _p("occupancy", F, "Occupancy", required=False, default=0.95),
        ],
    },
    # ── VC / Lending ──
    "vc_fund": {
        "name": "VC Fund Metrics",
        "module": "vc_returns",
        "fn": "fund_metrics",
        "category": "VC / Lending",
        "params": [
            _p("contributions", LF, "Contributions", hint="10,10,10"),
            _p("distributions", LF, "Distributions", hint="0,0,5"),
            _p("nav", F, "Current NAV"),
            _p("years", F, "Fund Age (years)"),
        ],
    },
    "loan_amort": {
        "name": "Loan Amortization",
        "module": "loan_amort",
        "fn": "loan_amortization",
        "category": "VC / Lending",
        "params": [
            _p("principal", F, "Principal"),
            _p("annual_rate", F, "Annual Rate", hint="0.065"),
            _p("years", I, "Term (years)", hint="30"),
            _p("extra_payment", F, "Extra Payment", required=False, default=0),
        ],
    },
    "depreciation": {
        "name": "Depreciation (MACRS)",
        "module": "depreciation",
        "fn": "macrs",
        "category": "Valuation",
        "params": [
            _p("cost", F, "Asset Cost"),
            _p("recovery_period", I, "Recovery Period", hint="5, 7, 15, 27, or 39"),
            _p("bonus_pct", F, "Bonus %", required=False, default=0.0),
        ],
    },
}


def get_tools_by_category() -> dict[str, list[dict]]:
    """Return tools grouped by category, in display order."""
    grouped = {cat: [] for cat in CATEGORIES}
    for key, tool in TOOLS.items():
        cat = tool["category"]
        if cat in grouped:
            grouped[cat].append({"key": key, **tool})
    return {k: v for k, v in grouped.items() if v}


def import_tool(tool_key: str):
    """Lazily import and return a tool's function."""
    spec = TOOLS[tool_key]
    mod = importlib.import_module(spec["module"])
    return getattr(mod, spec["fn"])


def parse_param(value: str, param_type: str):
    """Convert a string input to the appropriate Python type."""
    if not value or not value.strip():
        return None
    value = value.strip()
    if param_type == "float":
        return float(value)
    if param_type == "int":
        return int(value)
    if param_type == "str":
        return value
    if param_type == "list[float]":
        return [float(x.strip()) for x in value.split(",")]
    if param_type == "list[list[float]]":
        import ast
        return ast.literal_eval(value)
    if param_type == "list[dict]":
        import ast
        return ast.literal_eval(value)
    if param_type == "list[tuple]":
        import ast
        return ast.literal_eval(value)
    return value
