"""Bloomberg-style command input bar."""

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Input, Static

from tui.theme import AMBER


class CommandBar(Widget):
    """Command bar at the bottom of every screen."""

    DEFAULT_CSS = """
    CommandBar {
        dock: bottom;
        height: 3;
        background: #000000;
        border-top: solid #3a3f5c;
        padding: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Static(f"[bold {AMBER}]CMD>[/] ", classes="cmd-label")
            yield Input(placeholder="Type a command (DCF, WIKI, TOOLS...)", id="cmd-input")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        cmd = event.value.strip().upper()
        event.input.value = ""

        screen_map = {
            "HOME": "dashboard", "DASHBOARD": "dashboard",
            "WIKI": "wiki",
            "TOOLS": "tools", "TOOL": "tools",
            "IDEAS": "ideas", "IDEA": "ideas", "MAP": "ideas",
        }

        if cmd in screen_map:
            self.app.action_switch_screen(screen_map[cmd])
        elif cmd:
            # Try to match a tool name
            from tui.registry import TOOLS
            for key, tool in TOOLS.items():
                if cmd == key.upper() or cmd == tool["name"].upper():
                    self.app.action_switch_screen("tools")
                    # Post a message to select the tool
                    if hasattr(self.app.screen, "select_tool"):
                        self.app.screen.select_tool(key)
                    break
