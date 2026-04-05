"""Dynamic parameter form builder for tools."""

from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widget import Widget
from textual.widgets import Button, Input, Static

from tui.registry import TOOLS, parse_param
from tui.theme import AMBER, MUTED


class ToolForm(Widget):
    """Dynamically generated input form for a tool's parameters."""

    DEFAULT_CSS = """
    ToolForm {
        height: auto;
        padding: 1 2;
    }
    """

    def __init__(self, tool_key: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.tool_key = tool_key
        self._inputs: dict[str, Input] = {}

    def compose(self) -> ComposeResult:
        if not self.tool_key or self.tool_key not in TOOLS:
            yield Static(f"[{MUTED}]Select a tool from the sidebar[/]")
            return

        tool = TOOLS[self.tool_key]
        yield Static(f"[bold {AMBER}]{tool['name']}[/]\n")

        for param in tool["params"]:
            default = str(param["default"]) if param.get("default") is not None else ""
            hint = param.get("hint", "")
            placeholder = hint or (f"default: {default}" if default else "")
            label_text = param["label"]
            if param["required"]:
                label_text += " *"

            with Horizontal(classes="form-row"):
                yield Static(f"[{AMBER}]{label_text:<20s}[/]", classes="form-label")
                inp = Input(
                    value=default,
                    placeholder=placeholder,
                    id=f"param-{param['name']}",
                )
                self._inputs[param["name"]] = inp
                yield inp

        yield Static("")
        with Horizontal():
            yield Button("Run", variant="primary", id="btn-run")
            yield Button("Clear", id="btn-clear")
            yield Button("Save to Session", id="btn-save")

    def get_params(self) -> dict | None:
        """Parse all inputs and return kwargs dict for the tool function."""
        if not self.tool_key:
            return None
        tool = TOOLS[self.tool_key]
        kwargs = {}
        for param in tool["params"]:
            inp = self._inputs.get(param["name"])
            if not inp:
                continue
            val = inp.value.strip()
            if not val:
                if param["required"]:
                    raise ValueError(f"'{param['label']}' is required")
                continue
            try:
                kwargs[param["name"]] = parse_param(val, param["type"])
            except (ValueError, SyntaxError) as e:
                raise ValueError(f"Invalid '{param['label']}': {e}")
        return kwargs

    def clear_inputs(self):
        for inp in self._inputs.values():
            inp.value = ""
