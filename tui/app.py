"""Main Alpha Stack TUI application."""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding

from tui.screens.dashboard import DashboardScreen
from tui.screens.idea_map import IdeaMapScreen
from tui.screens.tool_runner import ToolRunnerScreen
from tui.screens.wiki_browser import WikiBrowserScreen

CSS_PATH = Path(__file__).parent / "bloomberg.tcss"


class AlphaStackApp(App):
    """Bloomberg Terminal-inspired TUI for Alpha Stack."""

    TITLE = "ALPHA STACK"
    CSS_PATH = CSS_PATH

    BINDINGS = [
        Binding("f1", "switch_screen('dashboard')", "HOME", show=True),
        Binding("f2", "switch_screen('wiki')", "WIKI", show=True),
        Binding("f3", "switch_screen('tools')", "TOOLS", show=True),
        Binding("f4", "switch_screen('ideas')", "IDEAS", show=True),
        Binding("ctrl+q", "quit", "Quit", show=True),
        Binding("ctrl+r", "refresh_data", "Refresh", show=False),
    ]

    SCREENS = {
        "dashboard": DashboardScreen,
        "wiki": WikiBrowserScreen,
        "tools": ToolRunnerScreen,
        "ideas": IdeaMapScreen,
    }

    def on_mount(self) -> None:
        self.push_screen("dashboard")

    def action_switch_screen(self, screen: str) -> None:
        """Switch to a named screen."""
        # Pop all screens back to base, then push the requested one
        while len(self.screen_stack) > 1:
            self.pop_screen()
        if screen in self.SCREENS:
            self.push_screen(screen)

    def action_refresh_data(self) -> None:
        """Refresh market data on the current screen."""
        if hasattr(self.screen, "refresh_data"):
            self.screen.refresh_data()
