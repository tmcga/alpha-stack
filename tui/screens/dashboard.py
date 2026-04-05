"""Dashboard — HOME screen with wiki status, sessions, and market data."""

from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Static

from tui.theme import AMBER, GREEN, RED, MUTED
from tui.widgets.command_bar import CommandBar
from tui.widgets.ticker_bar import TickerBar


class DashboardScreen(Screen):
    """Main dashboard — the HOME screen."""

    def compose(self) -> ComposeResult:
        today = datetime.now().strftime("%Y-%m-%d")
        yield Static(
            f"[bold {AMBER}] ALPHA STACK[/]"
            f"[{MUTED}]{'':>50}{today}[/]",
            id="header",
        )
        yield Static(
            f"[{AMBER}] F1:HOME  F2:WIKI  F3:TOOLS  F4:IDEAS"
            f"{'':>30}Ctrl+Q:Quit[/]",
            id="fn-bar",
        )

        with Horizontal(id="dashboard-top"):
            with Vertical(classes="dash-panel"):
                yield Static(f"[bold {AMBER}]MARKETS[/]\n", classes="title")
                yield Static(f"[{MUTED}]Loading...[/]", id="market-indices")

            with Vertical(classes="dash-panel"):
                yield Static(f"[bold {AMBER}]TREASURY YIELD CURVE[/]\n", classes="title")
                yield Static(f"[{MUTED}]Loading...[/]", id="yield-data")

        with Horizontal(id="dashboard-bottom"):
            with Vertical(classes="dash-panel"):
                yield Static(f"[bold {AMBER}]WIKI[/]\n", classes="title")
                yield Static(f"[{MUTED}]Loading...[/]", id="wiki-status")

            with Vertical(classes="dash-panel"):
                yield Static(f"[bold {AMBER}]RECENT SESSIONS[/]\n", classes="title")
                yield Static(f"[{MUTED}]Loading...[/]", id="session-list")

        yield TickerBar()
        yield CommandBar()

    def on_mount(self) -> None:
        self._load_local_data()
        self._load_market_data()

    def _load_local_data(self) -> None:
        """Load wiki status and sessions (fast, local filesystem)."""
        try:
            from wiki import wiki_status
            status = wiki_status()
            if status.get("initialized"):
                pages = status["pages"]
                text = (
                    f"  Entities:   {pages.get('entities', 0):>4}\n"
                    f"  Playbooks:  {pages.get('playbooks', 0):>4}\n"
                    f"  Journal:    {pages.get('journal', 0):>4}\n"
                    f"  [{MUTED}]{'─' * 25}[/]\n"
                    f"  Total: {status['total_pages']} pages ({status['total_size_kb']} KB)\n"
                )
                if status.get("last_activity"):
                    text += f"  [{MUTED}]Last: {status['last_activity'][:40]}[/]"
            else:
                text = f"  [{MUTED}]Not initialized. Run /wiki init[/]"
            self.query_one("#wiki-status", Static).update(text)
        except Exception:
            self.query_one("#wiki-status", Static).update(f"  [{MUTED}]Wiki unavailable[/]")

        try:
            from state import list_sessions
            result = list_sessions()
            sessions = result.get("sessions", [])
            if sessions:
                lines = []
                for s in sessions[:8]:
                    date = s["saved_at"][:10] if s.get("saved_at") else "?"
                    tags = f"[{','.join(s.get('tags', []))}]" if s.get("tags") else ""
                    lines.append(f"  {s['name']:<22s} {date}  {tags}")
                text = "\n".join(lines)
            else:
                text = f"  [{MUTED}]No saved sessions[/]"
            self.query_one("#session-list", Static).update(text)
        except Exception:
            self.query_one("#session-list", Static).update(f"  [{MUTED}]Sessions unavailable[/]")

    def _load_market_data(self) -> None:
        """Fetch market data in background workers."""
        self.run_worker(self._fetch_indices, thread=True)
        self.run_worker(self._fetch_treasury, thread=True)

    async def _fetch_indices(self) -> None:
        """Fetch major market indices via yfinance."""
        try:
            from tui.data import get_index_snapshot, is_available
            if not is_available():
                self.app.call_from_thread(
                    self.query_one("#market-indices", Static).update,
                    f"  [{MUTED}]yfinance not installed[/]",
                )
                return

            indices = get_index_snapshot()
            lines = []
            for idx in indices:
                if "error" in idx:
                    lines.append(f"  {idx.get('name', idx['ticker']):<12s} [{MUTED}]unavailable[/]")
                    continue
                price = idx.get("price")
                chg = idx.get("change", 0)
                chg_pct = idx.get("change_pct", 0)
                color = GREEN if chg >= 0 else RED
                sign = "+" if chg >= 0 else ""
                if price and price > 1000:
                    price_str = f"{price:>10,.0f}"
                elif price:
                    price_str = f"{price:>10.2f}"
                else:
                    price_str = f"{'N/A':>10}"
                lines.append(
                    f"  {idx.get('name', idx['ticker']):<12s}"
                    f" {price_str}"
                    f"  [{color}]{sign}{chg:>8.2f}  ({sign}{chg_pct:.2f}%)[/]"
                )
            text = "\n".join(lines)
            updated = indices[0].get("updated", "") if indices else ""
            if updated:
                text += f"\n\n  [{MUTED}]Updated {updated}[/]"

            self.app.call_from_thread(self.query_one("#market-indices", Static).update, text)

            # Also update the ticker bar
            self.app.call_from_thread(
                self.query_one(TickerBar).update_indices, indices
            )
        except Exception as e:
            self.app.call_from_thread(
                self.query_one("#market-indices", Static).update,
                f"  [{MUTED}]Failed: {e}[/]",
            )

    async def _fetch_treasury(self) -> None:
        try:
            from fetch import treasury_rates
            rates = treasury_rates()
            if "rates" in rates:
                tenors = ["1 Mo", "3 Mo", "6 Mo", "1 Yr", "2 Yr", "5 Yr", "10 Yr", "20 Yr", "30 Yr"]
                lines = []
                for t in tenors:
                    val = rates["rates"].get(t)
                    if val is not None:
                        lines.append(f"  {t:<8s} {val:>7.3f}%")
                text = "\n".join(lines)
                date = rates.get("date", "")
                if date:
                    text += f"\n\n  [{MUTED}]As of {date}[/]"
            else:
                text = f"  [{MUTED}]{rates.get('error', 'No data')}[/]"
            self.app.call_from_thread(self.query_one("#yield-data", Static).update, text)
        except Exception as e:
            self.app.call_from_thread(
                self.query_one("#yield-data", Static).update,
                f"  [{MUTED}]Failed to fetch: {e}[/]",
            )

    def refresh_data(self) -> None:
        """Called by Ctrl+R."""
        self._load_local_data()
        self._load_market_data()
