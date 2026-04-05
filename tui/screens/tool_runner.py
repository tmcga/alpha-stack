"""Tool Runner — interactive tool execution with dynamic forms."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Static, Tree, Button

from tui.registry import TOOLS, get_tools_by_category, import_tool
from tui.theme import AMBER
from tui.widgets.command_bar import CommandBar
from tui.widgets.result_panel import ResultPanel
from tui.widgets.ticker_bar import TickerBar
from tui.widgets.tool_form import ToolForm


class ToolRunnerScreen(Screen):
    """Interactive tool execution screen."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._current_tool: str | None = None
        self._last_result: dict | None = None

    def compose(self) -> ComposeResult:
        yield Static(
            f"[bold {AMBER}] TOOL RUNNER[/]",
            id="header",
        )
        yield Static(
            f"[{AMBER}] F1:HOME  F2:WIKI  F3:TOOLS  F4:IDEAS"
            f"{'':>20}Ctrl+Enter:Run  Ctrl+Q:Quit[/]",
            id="fn-bar",
        )

        with Horizontal(id="tool-runner"):
            with Vertical(id="tool-sidebar"):
                yield Static(f"[bold {AMBER}]TOOLS[/]\n")
                tree = Tree("Tools", id="tool-tree")
                tree.show_root = False
                for cat, tools in get_tools_by_category().items():
                    branch = tree.root.add(f"[{AMBER}]{cat}[/]")
                    for t in tools:
                        branch.add_leaf(t["name"], data=t["key"])
                yield tree

            with Vertical(id="tool-main"):
                yield ToolForm(id="tool-form")
                yield ResultPanel(id="tool-results")

        yield TickerBar()
        yield CommandBar()

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """When a tool is selected in the sidebar tree."""
        if event.node.data and event.node.data in TOOLS:
            self.select_tool(event.node.data)

    def select_tool(self, tool_key: str) -> None:
        """Load a tool's form into the form area."""
        self._current_tool = tool_key
        # Replace the form widget
        old_form = self.query_one("#tool-form", ToolForm)
        new_form = ToolForm(tool_key=tool_key, id="tool-form")
        old_form.remove()
        self.query_one("#tool-main", Vertical).mount(new_form, before=self.query_one("#tool-results"))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-run":
            self._run_tool()
        elif event.button.id == "btn-clear":
            form = self.query_one("#tool-form", ToolForm)
            form.clear_inputs()
        elif event.button.id == "btn-save":
            self._save_result()

    def _run_tool(self) -> None:
        """Execute the current tool with form inputs."""
        if not self._current_tool:
            return
        form = self.query_one("#tool-form", ToolForm)
        result_panel = self.query_one("#tool-results", ResultPanel)

        try:
            kwargs = form.get_params()
            if kwargs is None:
                return
        except ValueError as e:
            result_panel.show_error(str(e))
            return

        # Run in worker thread to avoid blocking UI
        self.run_worker(self._execute_tool, self._current_tool, kwargs, thread=True)

    async def _execute_tool(self, tool_key: str, kwargs: dict) -> None:
        """Execute tool in background thread."""
        result_panel = self.query_one("#tool-results", ResultPanel)
        try:
            fn = import_tool(tool_key)
            result = fn(**kwargs)
            self._last_result = result
            tool_name = TOOLS[tool_key]["name"]
            self.app.call_from_thread(result_panel.show_result, tool_name, result)
        except Exception as e:
            self.app.call_from_thread(result_panel.show_error, f"{type(e).__name__}: {e}")

    def _save_result(self) -> None:
        """Save the last result to a session."""
        if not self._last_result or not self._current_tool:
            return
        try:
            from state import save_session
            name = f"{self._current_tool}-tui"
            result = save_session(name, self._last_result, tags=[self._current_tool])
            rp = self.query_one("#tool-results", ResultPanel)
            rp.show_result("Session Saved", {"name": result.get("name", name), "status": "saved"})
        except Exception as e:
            self.query_one("#tool-results", ResultPanel).show_error(f"Save failed: {e}")
