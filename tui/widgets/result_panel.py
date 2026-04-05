"""Formatted tool output display panel."""

import json

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static

from tui.theme import GREEN, RED, AMBER, MUTED


class ResultPanel(Widget):
    """Displays tool results in Bloomberg-style formatting."""

    DEFAULT_CSS = """
    ResultPanel {
        height: 1fr;
        padding: 1 2;
        overflow-y: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static(f"[{MUTED}]Run a tool to see results here[/]", id="result-content")

    def show_result(self, tool_name: str, result: dict):
        """Format and display a tool's result dict."""
        content = self.query_one("#result-content", Static)
        lines = [f"[bold {AMBER}]{'═' * 50}[/]"]
        lines.append(f"[bold {AMBER}]  {tool_name}[/]")
        lines.append(f"[bold {AMBER}]{'═' * 50}[/]\n")
        lines.extend(self._format_dict(result))
        content.update("\n".join(lines))

    def show_error(self, error: str):
        content = self.query_one("#result-content", Static)
        content.update(f"[bold {RED}]Error:[/] {error}")

    def _format_dict(self, d: dict, indent: int = 0) -> list[str]:
        """Recursively format a dict into display lines."""
        lines = []
        prefix = "  " * indent
        for key, val in d.items():
            label = key.replace("_", " ").title()
            if isinstance(val, dict):
                lines.append(f"{prefix}[{AMBER}]{label}:[/]")
                lines.extend(self._format_dict(val, indent + 1))
            elif isinstance(val, list):
                if val and isinstance(val[0], dict):
                    lines.append(f"{prefix}[{AMBER}]{label}:[/]")
                    for i, item in enumerate(val):
                        lines.append(f"{prefix}  [{MUTED}]#{i + 1}[/]")
                        lines.extend(self._format_dict(item, indent + 2))
                else:
                    formatted = ", ".join(f"{v}" for v in val[:20])
                    if len(val) > 20:
                        formatted += f" ... ({len(val)} items)"
                    lines.append(f"{prefix}  {label:<24s}  {formatted}")
            elif isinstance(val, float):
                color = GREEN if val > 0 else RED if val < 0 else ""
                if "pct" in key or "rate" in key or "return" in key or "yield" in key:
                    formatted = f"{val * 100:.2f}%" if abs(val) < 2 else f"{val:.2f}%"
                elif "price" in key or "value" in key or "cost" in key or "debt" in key:
                    formatted = f"${val:>14,.2f}"
                else:
                    formatted = f"{val:>14,.4f}"
                if color:
                    lines.append(f"{prefix}  {label:<24s}  [{color}]{formatted}[/]")
                else:
                    lines.append(f"{prefix}  {label:<24s}  {formatted}")
            elif isinstance(val, (int, bool)):
                lines.append(f"{prefix}  {label:<24s}  {val}")
            elif isinstance(val, str):
                lines.append(f"{prefix}  {label:<24s}  {val}")
            elif val is None:
                lines.append(f"{prefix}  {label:<24s}  [{MUTED}]—[/]")
        return lines

    def show_json(self, result: dict):
        """Show raw JSON fallback."""
        content = self.query_one("#result-content", Static)
        content.update(json.dumps(result, indent=2, default=str))
