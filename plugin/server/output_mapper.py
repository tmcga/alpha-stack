"""Maps tool result dicts to Excel cell range layouts.

Determines number formats, label positioning, and table structure
for writing tool results to Excel via Office.js.
"""


def detect_format(key: str, value) -> str:
    """Detect the appropriate Excel number format for a result value based on its key name.

    Mirrors the heuristics in tui/widgets/result_panel.py lines 60-74.
    """
    k = key.lower()

    # Percentage values
    if any(p in k for p in ("pct", "rate", "return", "yield", "margin", "growth", "probability",
                             "irr", "wacc", "spread", "win_rate", "occupancy")):
        return "0.0%"

    # Currency values
    if any(p in k for p in ("price", "value", "cost", "debt", "equity", "ev", "loan",
                             "noi", "revenue", "ebitda", "income", "payment", "interest",
                             "principal", "balance", "distribution", "promote", "nav",
                             "contribution", "withdrawal", "terminal")):
        if isinstance(value, (int, float)) and abs(value) >= 1_000_000:
            return "$#,##0"
        return "$#,##0.00"

    # Multiples
    if any(p in k for p in ("moic", "multiple", "tvpi", "dpi", "rvpi", "ratio",
                             "sharpe", "sortino", "calmar", "beta", "leverage")):
        return "0.00x"

    # Integers
    if isinstance(value, int) or (isinstance(value, float) and value == int(value) and abs(value) < 10000):
        if any(p in k for p in ("year", "month", "day", "period", "count", "sim")):
            return "0"

    # Default
    if isinstance(value, float):
        return "#,##0.0000"
    return "@"


def map_result_to_cells(tool_key: str, result: dict) -> list[dict]:
    """Convert a flat or nested tool result dict into a list of cell write operations.

    Returns list of: {"row": int, "col": str, "label": str, "value": any, "format": str}
    Rows start at 1 (header), data from row 3.
    """
    cells = []
    row = 3

    for key, value in result.items():
        if isinstance(value, dict):
            # Nested section (e.g., attribution, npv_table)
            cells.append({"row": row, "col": "A", "label": key.replace("_", " ").title(),
                          "value": "", "format": "@", "style": "section_header"})
            row += 1
            for sub_key, sub_val in value.items():
                if isinstance(sub_val, (int, float, str, bool)) or sub_val is None:
                    cells.append({
                        "row": row, "col": "A", "label": f"  {sub_key.replace('_', ' ').title()}",
                        "value": sub_val if sub_val is not None else "",
                        "value_col": "B",
                        "format": detect_format(sub_key, sub_val),
                    })
                    row += 1
            row += 1  # Blank row after section

        elif isinstance(value, list):
            if not value:
                continue
            if isinstance(value[0], dict):
                # Table of dicts (e.g., yearly waterfall data, schedule)
                cells.append({"row": row, "col": "A", "label": key.replace("_", " ").title(),
                              "value": "", "format": "@", "style": "section_header"})
                row += 1
                # Header row
                headers = list(value[0].keys())
                for col_idx, header in enumerate(headers):
                    col_letter = chr(65 + col_idx)  # A, B, C, ...
                    cells.append({
                        "row": row, "col": col_letter,
                        "label": header.replace("_", " ").title(),
                        "value": header.replace("_", " ").title(),
                        "format": "@", "style": "table_header",
                    })
                row += 1
                # Data rows
                for item in value[:50]:  # Cap at 50 rows
                    for col_idx, (h, v) in enumerate(item.items()):
                        col_letter = chr(65 + col_idx)
                        cells.append({
                            "row": row, "col": col_letter,
                            "label": "", "value": v,
                            "format": detect_format(h, v),
                        })
                    row += 1
                row += 1
            else:
                # Simple list (e.g., debt_schedule as list of floats)
                cells.append({"row": row, "col": "A", "label": key.replace("_", " ").title(),
                              "value": "", "format": "@", "style": "section_header"})
                row += 1
                for i, v in enumerate(value[:50]):
                    cells.append({
                        "row": row, "col": "A", "label": str(i),
                        "value": v, "value_col": "B",
                        "format": detect_format(key, v),
                    })
                    row += 1
                row += 1

        elif isinstance(value, (int, float, str, bool)) or value is None:
            cells.append({
                "row": row, "col": "A",
                "label": key.replace("_", " ").title(),
                "value": value if value is not None else "",
                "value_col": "B",
                "format": detect_format(key, value),
            })
            row += 1

    return cells
