"""Model template definitions for the Excel Add-in.

Each template defines: metadata, sheet structure, input cell specs (yellow-shaded),
output cell specs (where tool results write), and the tools used.
"""

TEMPLATES = {
    "lbo_model": {
        "name": "LBO Model",
        "description": "Full leveraged buyout model with debt schedule and returns attribution",
        "tools": ["lbo"],
        "sheets": ["Assumptions", "Sources & Uses", "Debt Schedule", "Returns", "Sensitivity"],
        "inputs": {
            "sheet": "Assumptions",
            "cells": [
                {"cell": "B3", "label": "EBITDA", "param": "ebitda", "format": "$#,##0", "default": 100},
                {"cell": "B4", "label": "Entry Multiple", "param": "entry_multiple", "format": "0.0x", "default": 10},
                {"cell": "B5", "label": "Exit Multiple", "param": "exit_multiple", "format": "0.0x", "default": 11},
                {"cell": "B6", "label": "Leverage (x EBITDA)", "param": "leverage", "format": "0.0x", "default": 5},
                {"cell": "B7", "label": "Interest Rate", "param": "interest_rate", "format": "0.0%", "default": 0.06},
                {"cell": "B8", "label": "EBITDA Growth", "param": "ebitda_growth", "format": "0.0%", "default": 0.08},
                {"cell": "B9", "label": "Hold Period (years)", "param": "years", "format": "0", "default": 5},
                {"cell": "B10", "label": "Amortization %", "param": "amortization_pct", "format": "0.0%", "default": 0.01},
            ],
        },
        "outputs": {
            "sources_uses": {
                "sheet": "Sources & Uses",
                "cells": [
                    {"cell": "B3", "key": "entry_ev", "label": "Enterprise Value", "format": "$#,##0"},
                    {"cell": "B4", "key": "entry_debt", "label": "Debt", "format": "$#,##0"},
                    {"cell": "B5", "key": "entry_equity", "label": "Sponsor Equity", "format": "$#,##0"},
                ],
            },
            "returns": {
                "sheet": "Returns",
                "cells": [
                    {"cell": "B3", "key": "moic", "label": "MOIC", "format": "0.00x"},
                    {"cell": "B4", "key": "irr", "label": "IRR", "format": "0.0%"},
                    {"cell": "B5", "key": "exit_ev", "label": "Exit EV", "format": "$#,##0"},
                    {"cell": "B6", "key": "exit_equity", "label": "Exit Equity", "format": "$#,##0"},
                    {"cell": "B7", "key": "debt_paydown", "label": "Debt Paydown", "format": "$#,##0"},
                ],
            },
            "attribution": {
                "sheet": "Returns",
                "start": "B10",
                "cells": [
                    {"key": "attribution.ebitda_growth", "label": "EBITDA Growth", "format": "0.0%"},
                    {"key": "attribution.multiple_change", "label": "Multiple Expansion", "format": "0.0%"},
                    {"key": "attribution.deleveraging", "label": "Deleveraging", "format": "0.0%"},
                ],
            },
            "debt_schedule": {
                "sheet": "Debt Schedule",
                "type": "table",
                "headers": ["Year", "EBITDA", "Debt Balance"],
                "data_keys": ["ebitda_schedule", "debt_schedule"],
                "formats": ["0", "$#,##0", "$#,##0"],
            },
        },
        "sensitivity": {
            "sheet": "Sensitivity",
            "output_key": "irr",
            "output_format": "0.0%",
            "row_param": "entry_multiple",
            "row_label": "Entry Multiple",
            "row_values": [8, 9, 10, 11, 12],
            "col_param": "exit_multiple",
            "col_label": "Exit Multiple",
            "col_values": [9, 10, 11, 12, 13],
        },
    },
    "dcf_model": {
        "name": "DCF Model",
        "description": "Discounted cash flow valuation with WACC build-up and sensitivity",
        "tools": ["dcf", "wacc"],
        "sheets": ["Assumptions", "FCF Build", "DCF Output", "WACC", "Sensitivity"],
        "inputs": {
            "sheet": "Assumptions",
            "cells": [
                {"cell": "B3", "label": "Base FCF", "param": "base_fcf", "format": "$#,##0", "default": 100},
                {"cell": "B4", "label": "FCF Growth Rate", "param": "growth", "format": "0.0%", "default": 0.10},
                {"cell": "B5", "label": "Projection Years", "param": "years", "format": "0", "default": 5},
                {"cell": "B6", "label": "WACC", "param": "wacc", "format": "0.0%", "default": 0.10},
                {"cell": "B7", "label": "Terminal Growth", "param": "terminal_growth", "format": "0.0%", "default": 0.025},
                {"cell": "B8", "label": "Net Debt", "param": "net_debt", "format": "$#,##0", "default": 500},
                {"cell": "B9", "label": "Shares Outstanding", "param": "shares", "format": "#,##0", "default": 100},
            ],
        },
        "outputs": {
            "dcf": {
                "sheet": "DCF Output",
                "cells": [
                    {"cell": "B3", "key": "enterprise_value", "label": "Enterprise Value", "format": "$#,##0.00"},
                    {"cell": "B4", "key": "equity_value", "label": "Equity Value", "format": "$#,##0.00"},
                    {"cell": "B5", "key": "price_per_share", "label": "Price per Share", "format": "$#,##0.00"},
                    {"cell": "B6", "key": "pv_explicit_fcfs", "label": "PV of Explicit FCFs", "format": "$#,##0.00"},
                    {"cell": "B7", "key": "pv_terminal_value", "label": "PV of Terminal Value", "format": "$#,##0.00"},
                    {"cell": "B8", "key": "terminal_value_pct", "label": "Terminal Value % of EV", "format": "0.0%"},
                ],
            },
        },
        "sensitivity": {
            "sheet": "Sensitivity",
            "output_key": "price_per_share",
            "output_format": "$#,##0.00",
            "row_param": "wacc",
            "row_label": "WACC",
            "row_values": [0.08, 0.09, 0.10, 0.11, 0.12],
            "col_param": "terminal_growth",
            "col_label": "Terminal Growth",
            "col_values": [0.015, 0.020, 0.025, 0.030, 0.035],
        },
    },
    "debt_sizing_model": {
        "name": "Debt Sizing",
        "description": "CRE debt sizing across DSCR, LTV, and debt yield constraints",
        "tools": ["re_debt", "loan_amort"],
        "sheets": ["Assumptions", "Constraints", "Amortization", "Sensitivity"],
        "inputs": {
            "sheet": "Assumptions",
            "cells": [
                {"cell": "B3", "label": "NOI", "param": "noi", "format": "$#,##0", "default": 1800000},
                {"cell": "B4", "label": "Property Value", "param": "property_value", "format": "$#,##0", "default": 28000000},
                {"cell": "B5", "label": "Interest Rate", "param": "rate", "format": "0.00%", "default": 0.0625},
                {"cell": "B6", "label": "Max LTV", "param": "max_ltv", "format": "0.0%", "default": 0.65},
                {"cell": "B7", "label": "Min DSCR", "param": "min_dscr", "format": "0.00x", "default": 1.25},
            ],
        },
        "outputs": {
            "sizing": {
                "sheet": "Constraints",
                "cells": [
                    {"cell": "B3", "key": "max_loan", "label": "Max Loan Proceeds", "format": "$#,##0"},
                    {"cell": "B4", "key": "binding_constraint", "label": "Binding Constraint", "format": "@"},
                    {"cell": "B5", "key": "actual_ltv", "label": "Actual LTV", "format": "0.0%"},
                    {"cell": "B6", "key": "actual_dscr", "label": "Actual DSCR", "format": "0.00x"},
                    {"cell": "B7", "key": "actual_debt_yield", "label": "Debt Yield", "format": "0.0%"},
                    {"cell": "B8", "key": "positive_leverage", "label": "Positive Leverage?", "format": "@"},
                ],
            },
        },
        "sensitivity": {
            "sheet": "Sensitivity",
            "output_key": "max_loan",
            "output_format": "$#,##0",
            "row_param": "rate",
            "row_label": "Interest Rate",
            "row_values": [0.050, 0.055, 0.0625, 0.070, 0.075],
            "col_param": "max_ltv",
            "col_label": "Max LTV",
            "col_values": [0.55, 0.60, 0.65, 0.70, 0.75],
        },
    },
    "waterfall_model": {
        "name": "Equity Waterfall",
        "description": "RE equity waterfall with LP/GP promote tiers and IRR/MOIC",
        "tools": ["re_waterfall"],
        "sheets": ["Deal Summary", "Cash Flows", "LP/GP Splits", "Returns"],
        "inputs": {
            "sheet": "Deal Summary",
            "cells": [
                {"cell": "B3", "label": "Total Equity", "param": "equity_invested", "format": "$#,##0", "default": 10000000},
                {"cell": "B4", "label": "LP Share", "param": "lp_share", "format": "0.0%", "default": 0.90},
                {"cell": "B5", "label": "Preferred Return", "param": "pref_rate", "format": "0.0%", "default": 0.08},
            ],
        },
        "outputs": {
            "returns": {
                "sheet": "Returns",
                "cells": [
                    {"cell": "B3", "key": "project_irr", "label": "Project IRR", "format": "0.0%"},
                    {"cell": "B4", "key": "lp_irr", "label": "LP IRR", "format": "0.0%"},
                    {"cell": "B5", "key": "gp_irr", "label": "GP IRR", "format": "0.0%"},
                    {"cell": "B6", "key": "lp_multiple", "label": "LP Multiple", "format": "0.00x"},
                    {"cell": "B7", "key": "gp_multiple", "label": "GP Multiple", "format": "0.00x"},
                    {"cell": "B8", "key": "total_promote", "label": "Total GP Promote", "format": "$#,##0"},
                ],
            },
            "yearly": {
                "sheet": "LP/GP Splits",
                "type": "table",
                "headers": ["Year", "Cash Flow", "LP Distribution", "GP Distribution"],
                "data_keys": ["cash_flow", "lp_distribution", "gp_distribution"],
                "formats": ["0", "$#,##0", "$#,##0", "$#,##0"],
            },
        },
    },
    "merger_model": {
        "name": "Merger Model",
        "description": "M&A merger arb analysis with deal spread and implied probability",
        "tools": ["merger_arb"],
        "sheets": ["Deal Terms", "Spread Analysis"],
        "inputs": {
            "sheet": "Deal Terms",
            "cells": [
                {"cell": "B3", "label": "Current Price", "param": "current_price", "format": "$#,##0.00", "default": 45},
                {"cell": "B4", "label": "Offer Price", "param": "offer_price", "format": "$#,##0.00", "default": 50},
                {"cell": "B5", "label": "Days to Close", "param": "days_to_close", "format": "0", "default": 90},
                {"cell": "B6", "label": "Risk-Free Rate", "param": "risk_free", "format": "0.0%", "default": 0.05},
                {"cell": "B7", "label": "Downside Price", "param": "downside_price", "format": "$#,##0.00", "default": 38},
            ],
        },
        "outputs": {
            "spread": {
                "sheet": "Spread Analysis",
                "cells": [
                    {"cell": "B3", "key": "gross_spread", "label": "Gross Spread", "format": "0.0%"},
                    {"cell": "B4", "key": "annualized_spread", "label": "Annualized Spread", "format": "0.0%"},
                    {"cell": "B5", "key": "implied_probability", "label": "Implied Probability", "format": "0.0%"},
                    {"cell": "B6", "key": "breakeven_probability", "label": "Breakeven Probability", "format": "0.0%"},
                ],
            },
        },
    },
    "cap_table_model": {
        "name": "Cap Table",
        "description": "VC dilution waterfall with round-by-round ownership tracking",
        "tools": ["vc_fund"],
        "sheets": ["Fund Metrics"],
        "inputs": {
            "sheet": "Fund Metrics",
            "cells": [
                {"cell": "B3", "label": "Current NAV", "param": "nav", "format": "$#,##0", "default": 30000000},
                {"cell": "B4", "label": "Fund Age (years)", "param": "years", "format": "0.0", "default": 3},
            ],
        },
        "outputs": {
            "metrics": {
                "sheet": "Fund Metrics",
                "cells": [
                    {"cell": "B7", "key": "tvpi", "label": "TVPI", "format": "0.00x"},
                    {"cell": "B8", "key": "dpi", "label": "DPI", "format": "0.00x"},
                    {"cell": "B9", "key": "rvpi", "label": "RVPI", "format": "0.00x"},
                    {"cell": "B10", "key": "irr", "label": "Fund IRR", "format": "0.0%"},
                ],
            },
        },
    },
    "portfolio_risk_model": {
        "name": "Portfolio Risk",
        "description": "Portfolio risk analytics — Sharpe, Sortino, VaR, max drawdown",
        "tools": ["portfolio_risk"],
        "sheets": ["Returns", "Risk Metrics"],
        "inputs": {
            "sheet": "Returns",
            "cells": [
                {"cell": "B3", "label": "Risk-Free Rate", "param": "risk_free", "format": "0.0%", "default": 0.045},
                {"cell": "B4", "label": "Periods Per Year", "param": "periods_per_year", "format": "0", "default": 12},
            ],
        },
        "outputs": {
            "metrics": {
                "sheet": "Risk Metrics",
                "cells": [
                    {"cell": "B3", "key": "ann_return", "label": "Annualized Return", "format": "0.00%"},
                    {"cell": "B4", "key": "ann_volatility", "label": "Annualized Volatility", "format": "0.00%"},
                    {"cell": "B5", "key": "sharpe", "label": "Sharpe Ratio", "format": "0.00"},
                    {"cell": "B6", "key": "sortino", "label": "Sortino Ratio", "format": "0.00"},
                    {"cell": "B7", "key": "max_drawdown", "label": "Max Drawdown", "format": "0.00%"},
                    {"cell": "B8", "key": "var_95", "label": "VaR (95%)", "format": "0.00%"},
                    {"cell": "B9", "key": "cvar_95", "label": "CVaR (95%)", "format": "0.00%"},
                ],
            },
        },
    },
    "retirement_model": {
        "name": "Retirement Plan",
        "description": "Monte Carlo retirement planning with withdrawal strategy",
        "tools": ["monte_carlo"],
        "sheets": ["Assumptions", "Monte Carlo Results"],
        "inputs": {
            "sheet": "Assumptions",
            "cells": [
                {"cell": "B3", "label": "Initial Portfolio", "param": "initial", "format": "$#,##0", "default": 1000000},
                {"cell": "B4", "label": "Expected Return", "param": "expected_return", "format": "0.0%", "default": 0.07},
                {"cell": "B5", "label": "Volatility", "param": "volatility", "format": "0.0%", "default": 0.15},
                {"cell": "B6", "label": "Years", "param": "years", "format": "0", "default": 30},
                {"cell": "B7", "label": "Withdrawal Rate", "param": "withdrawal_rate", "format": "0.0%", "default": 0.04},
                {"cell": "B8", "label": "Simulations", "param": "num_sims", "format": "#,##0", "default": 10000},
            ],
        },
        "outputs": {
            "results": {
                "sheet": "Monte Carlo Results",
                "cells": [
                    {"cell": "B3", "key": "mean_terminal", "label": "Mean Terminal Value", "format": "$#,##0"},
                    {"cell": "B4", "key": "median_terminal", "label": "Median Terminal Value", "format": "$#,##0"},
                    {"cell": "B5", "key": "percentile_5", "label": "5th Percentile", "format": "$#,##0"},
                    {"cell": "B6", "key": "percentile_95", "label": "95th Percentile", "format": "$#,##0"},
                    {"cell": "B7", "key": "ruin_probability", "label": "Ruin Probability", "format": "0.0%"},
                ],
            },
        },
    },
    "operating_model": {
        "name": "Operating Model",
        "description": "Revenue build, P&L, and cash flow projection with IRR analysis",
        "tools": ["irr"],
        "sheets": ["Revenue Build", "P&L", "Cash Flow", "Returns"],
        "inputs": {
            "sheet": "Revenue Build",
            "cells": [
                {"cell": "B3", "label": "Year 1 Revenue", "param": "y1_revenue", "format": "$#,##0", "default": 10000000},
                {"cell": "B4", "label": "Growth Rate", "param": "growth_rate", "format": "0.0%", "default": 0.20},
                {"cell": "B5", "label": "Gross Margin", "param": "gross_margin", "format": "0.0%", "default": 0.65},
                {"cell": "B6", "label": "OpEx % of Revenue", "param": "opex_pct", "format": "0.0%", "default": 0.45},
            ],
        },
        "outputs": {},
    },
}
