"""Bloomberg color constants and value formatters."""

# Bloomberg palette
BG_NAVY = "#0a0e2a"
BG_PANEL = "#0d1230"
BG_HEADER = "#1a1f4a"
BG_CURSOR = "#2a2f6a"
BORDER = "#3a3f5c"
AMBER = "#ff9900"
GREEN = "#00c853"
RED = "#ff1744"
WHITE = "#e0e0e0"
BRIGHT = "#ffffff"
TERMINAL_GREEN = "#00ff41"
MUTED = "#6a6f8c"


def color_value(val: float) -> str:
    """Return rich markup color tag for a numeric value."""
    if val > 0:
        return f"[{GREEN}]+{val:,.2f}[/]"
    elif val < 0:
        return f"[{RED}]{val:,.2f}[/]"
    return f"[{WHITE}]{val:,.2f}[/]"


def fmt_pct(val: float) -> str:
    """Format percentage with sign and color."""
    pct = val * 100 if abs(val) < 1 else val
    if pct > 0:
        return f"[{GREEN}]+{pct:.2f}%[/]"
    elif pct < 0:
        return f"[{RED}]{pct:.2f}%[/]"
    return f"[{WHITE}]{pct:.2f}%[/]"


def fmt_currency(val: float) -> str:
    """Format currency value."""
    return f"${val:>14,.2f}"


def fmt_number(val: float, decimals: int = 2) -> str:
    """Format a plain number."""
    return f"{val:>12,.{decimals}f}"
