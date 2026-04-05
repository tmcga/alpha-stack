"""Bottom status bar with market data ticker."""

from datetime import datetime

from textual.widget import Widget
from textual.widgets import Static

from tui.theme import GREEN, RED


class TickerBar(Widget):
    """Single-line status bar showing key market data."""

    DEFAULT_CSS = """
    TickerBar {
        dock: bottom;
        height: 1;
        background: #0d1230;
        color: #6a6f8c;
        padding: 0 1;
        border-top: solid #3a3f5c;
    }
    """

    def compose(self):
        now = datetime.now().strftime("%H:%M")
        yield Static(
            f"  ALPHA STACK  │  F1:HOME  F2:WIKI  F3:TOOLS  F4:IDEAS  │  Ctrl+Q:Quit  │  {now}",
            id="ticker-text",
        )

    def update_indices(self, indices: list[dict]):
        """Update ticker with live index data."""
        parts = []
        for idx in indices:
            if "error" in idx or not idx.get("price"):
                continue
            name = idx.get("name", idx["ticker"])
            price = idx["price"]
            chg = idx.get("change_pct", 0)
            color = GREEN if chg >= 0 else RED
            sign = "+" if chg >= 0 else ""
            if price > 1000:
                parts.append(f"{name} {price:,.0f} [{color}]{sign}{chg:.2f}%[/]")
            else:
                parts.append(f"{name} {price:.2f} [{color}]{sign}{chg:.2f}%[/]")

        now = datetime.now().strftime("%H:%M")
        if parts:
            text = "  " + "  │  ".join(parts) + f"  │  {now}"
        else:
            text = f"  ALPHA STACK  │  F1:HOME  F2:WIKI  F3:TOOLS  F4:IDEAS  │  Ctrl+Q:Quit  │  {now}"
        self.query_one("#ticker-text", Static).update(text)

    def update_rates(self, rates: dict | None = None, fred: dict | None = None):
        """Update ticker with treasury/FRED data (fallback if no yfinance)."""
        parts = ["ALPHA STACK"]
        if rates and "rates" in rates:
            r = rates["rates"]
            if "10 Yr" in r:
                parts.append(f"10Y:{r['10 Yr']:.3f}%")
            if "2 Yr" in r:
                parts.append(f"2Y:{r['2 Yr']:.3f}%")
        if fred and "series" in fred:
            s = fred["series"]
            if "VIXCLS" in s and "value" in s["VIXCLS"]:
                parts.append(f"VIX:{s['VIXCLS']['value']}")
        now = datetime.now().strftime("%H:%M")
        parts.append(f"Ctrl+Q:Quit  │  {now}")
        self.query_one("#ticker-text", Static).update("  " + "  │  ".join(parts))
