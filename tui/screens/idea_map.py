"""Idea Map — intelligence layer that surfaces actionable ideas from the wiki."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Static, Tree

from tui.ideas import (
    Idea,
    IdeaType,
    IDEA_TYPE_LABELS,
    generate_ideas,
    enrich_with_market_data,
)
from tui.theme import AMBER, GREEN, RED, MUTED, BRIGHT, WHITE
from tui.widgets.command_bar import CommandBar
from tui.widgets.ticker_bar import TickerBar

# Map idea types to display colors
_TYPE_COLORS = {
    IdeaType.THESIS_DRIFT: AMBER,
    IdeaType.OUTCOME_TRACKER: GREEN,
    IdeaType.RESEARCH_GAP: MUTED,
    IdeaType.RISK_MONITOR: RED,
    IdeaType.SUGGESTED_ACTION: WHITE,
    IdeaType.STALE_PLAYBOOK: MUTED,
}

# Sidebar category display names
_SIDEBAR_CATEGORIES = [
    ("ALL", None),
    ("DRIFT", IdeaType.THESIS_DRIFT),
    ("OUTCOMES", IdeaType.OUTCOME_TRACKER),
    ("GAPS", IdeaType.RESEARCH_GAP),
    ("RISKS", IdeaType.RISK_MONITOR),
    ("ACTIONS", None),  # Combined: SUGGESTED_ACTION + STALE_PLAYBOOK
]


class IdeaMapScreen(Screen):
    """Idea Map — surfaces actionable ideas from wiki + market data."""

    BINDINGS = [
        ("1", "idea_action(0)", "Action 1"),
        ("2", "idea_action(1)", "Action 2"),
        ("3", "idea_action(2)", "Action 3"),
        ("4", "idea_action(3)", "Action 4"),
        ("j", "next_idea", "Next"),
        ("k", "prev_idea", "Prev"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ideas: list[Idea] = []
        self._selected: Idea | None = None
        self._filter_type: IdeaType | str | None = None  # None = ALL

    def compose(self) -> ComposeResult:
        yield Static(
            f"[bold {AMBER}] IDEA MAP[/]",
            id="header",
        )
        yield Static(
            f"[{AMBER}] F1:HOME  F2:WIKI  F3:TOOLS  F4:IDEAS"
            f"{'':>14}j/k:Nav  1-4:Act  Ctrl+R  Ctrl+Q[/]",
            id="fn-bar",
        )

        with Horizontal(id="idea-map"):
            with Vertical(id="idea-sidebar"):
                yield Static(f"[bold {AMBER}]CATEGORIES[/]\n", id="idea-categories")
                tree = Tree("Ideas", id="idea-tree")
                tree.show_root = False
                yield tree

            with Vertical(id="idea-detail"):
                yield Static(
                    f"[{MUTED}]Scanning wiki for ideas...[/]",
                    id="idea-content",
                )

        yield TickerBar()
        yield CommandBar()

    def on_mount(self) -> None:
        self.run_worker(self._load_ideas_async, thread=True)

    async def _load_ideas_async(self) -> None:
        """Generate ideas in a worker thread, then enrich with market data."""
        ideas = generate_ideas()
        self._ideas = ideas

        def _show_ideas():
            self._update_sidebar()
            if self._ideas:
                self._select_idea(self._ideas[0])
            else:
                self.query_one("#idea-content", Static).update(
                    f"[{MUTED}]No ideas generated. Build your wiki with /wiki to get started.[/]"
                )

        self.app.call_from_thread(_show_ideas)

        # Phase 3: enrich with market data
        enriched = enrich_with_market_data(self._ideas)
        self._ideas = enriched

        def _update_with_market():
            self._update_sidebar()
            if self._selected:
                for idea in self._ideas:
                    if idea.title == self._selected.title:
                        self._select_idea(idea)
                        return
                if self._ideas:
                    self._select_idea(self._ideas[0])

        self.app.call_from_thread(_update_with_market)

    def _update_sidebar(self) -> None:
        """Rebuild the category counts and idea tree."""
        # Count by category
        counts = {}
        for idea in self._ideas:
            label = IDEA_TYPE_LABELS.get(idea.idea_type, "OTHER")
            counts[label] = counts.get(label, 0) + 1

        # Build category text
        cat_lines = []
        for display_name, idea_type in _SIDEBAR_CATEGORIES:
            if display_name == "ALL":
                count = len(self._ideas)
                selected = self._filter_type is None
            elif display_name == "ACTIONS":
                count = counts.get("ACTIONS", 0)
                selected = self._filter_type == "ACTIONS"
            else:
                count = counts.get(display_name, 0)
                selected = self._filter_type == idea_type

            if count == 0 and display_name != "ALL":
                continue
            marker = ">" if selected else " "
            style = f"bold {BRIGHT}" if selected else AMBER
            cat_lines.append(f"  [{style}]{marker} {display_name} ({count})[/]")

        self.query_one("#idea-categories", Static).update(
            f"[bold {AMBER}]CATEGORIES[/]\n" + "\n".join(cat_lines) + f"\n[{MUTED}]{'─' * 22}[/]"
        )

        # Rebuild tree with filtered ideas
        filtered = self._get_filtered_ideas()
        tree = self.query_one("#idea-tree", Tree)
        tree.clear()
        for idea in filtered:
            color = _TYPE_COLORS.get(idea.idea_type, WHITE)
            # Truncate title to fit sidebar
            display = idea.title[:24]
            tree.root.add_leaf(f"[{color}]{display}[/]", data=idea)

    def _get_filtered_ideas(self) -> list[Idea]:
        if self._filter_type is None:
            return self._ideas
        if self._filter_type == "ACTIONS":
            return [i for i in self._ideas
                    if i.idea_type in (IdeaType.SUGGESTED_ACTION, IdeaType.STALE_PLAYBOOK)]
        return [i for i in self._ideas if i.idea_type == self._filter_type]

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        if event.node.data and isinstance(event.node.data, Idea):
            self._select_idea(event.node.data)

    def _select_idea(self, idea: Idea) -> None:
        """Display an idea's full detail in the main panel."""
        self._selected = idea
        content = self.query_one("#idea-content", Static)
        content.update(self._render_detail(idea))

    def _render_detail(self, idea: Idea) -> str:
        """Render a full idea detail view as Rich markup."""
        color = _TYPE_COLORS.get(idea.idea_type, WHITE)
        type_label = idea.idea_type.name.replace("_", " ")
        lines = [
            f"[bold {AMBER}]{'═' * 50}[/]",
            f"[bold {color}]  {type_label}: {idea.title}[/]",
            f"[bold {AMBER}]{'═' * 50}[/]",
        ]

        if idea.subtitle:
            lines.append(f"  [{MUTED}]{idea.subtitle}[/]")
        lines.append("")

        # Type-specific detail rendering
        d = idea.detail

        if idea.idea_type == IdeaType.THESIS_DRIFT:
            if d.get("thesis"):
                lines.append(f"  [{AMBER}]Thesis[/] ({d.get('date', '?')})")
                lines.append(f"  \"{d['thesis']}\"")
                lines.append("")

            if d.get("current_price"):
                target = d.get("target_price", 0)
                current = d["current_price"]
                drift = d.get("drift_pct", 0)
                drift_color = GREEN if drift >= 0 else RED
                sign = "+" if drift >= 0 else ""
                lines.append(f"  [{AMBER}]Price Comparison[/]")
                lines.append(f"    Target:    ${target:>12,.2f}")
                lines.append(f"    Current:   ${current:>12,.2f}")
                lines.append(f"    Drift:     [{drift_color}]{sign}{drift:.1%}[/]")
                lines.append("")
            elif d.get("target_price"):
                lines.append(f"  [{AMBER}]Target Price[/]: ${d['target_price']:,.2f}")
                lines.append(f"  [{MUTED}]Fetching current price...[/]")
                lines.append("")

            if d.get("direction"):
                lines.append(f"  [{AMBER}]Recommendation[/]")
                lines.append(f"    Direction:   {d['direction']}")
                if d.get("conviction"):
                    lines.append(f"    Conviction:  {d['conviction']}")
                if d.get("horizon_months"):
                    lines.append(f"    Horizon:     {d['horizon_months']:.0f} months")

        elif idea.idea_type == IdeaType.OUTCOME_TRACKER:
            if d.get("thesis"):
                lines.append(f"  [{AMBER}]Thesis[/]")
                lines.append(f"  \"{d['thesis']}\"")
                lines.append("")

            lines.append(f"  [{AMBER}]Position[/]")
            if d.get("direction"):
                lines.append(f"    Direction:   {d['direction']}")
            if d.get("target_price"):
                lines.append(f"    Target:      ${d['target_price']:>12,.2f}")
            if d.get("current_price"):
                pnl = d.get("pnl_pct", 0)
                pnl_color = GREEN if pnl >= 0 else RED
                sign = "+" if pnl >= 0 else ""
                lines.append(f"    Current:     ${d['current_price']:>12,.2f}")
                lines.append(f"    P&L:         [{pnl_color}]{sign}{pnl:.1%}[/]")
            lines.append("")
            lines.append(f"  [{AMBER}]Timeline[/]")
            lines.append(f"    Elapsed:     {d.get('days_elapsed', '?')} days")
            if d.get("horizon_months"):
                lines.append(f"    Horizon:     {d['horizon_months']:.0f} months")

        elif idea.idea_type == IdeaType.RESEARCH_GAP:
            if d.get("days_stale"):
                lines.append(f"  [{AMBER}]Staleness[/]")
                lines.append(f"    Days since update:  {d['days_stale']}")
                if d.get("last_updated"):
                    lines.append(f"    Last updated:       {d['last_updated']}")
            if d.get("missing_slug"):
                lines.append(f"  [{AMBER}]Missing Entity[/]")
                lines.append(f"    Slug:          {d['missing_slug']}")
                lines.append(f"    Referenced by:  {d.get('referenced_by', '?')}")

        elif idea.idea_type == IdeaType.RISK_MONITOR:
            if d.get("risk_text"):
                lines.append(f"  [{AMBER}]Risk Factor[/]")
                lines.append(f"  \"{d['risk_text']}\"")
                lines.append("")
            if d.get("frequency"):
                lines.append(f"  [{AMBER}]Frequency[/]: Flagged {d['frequency']}x across analyses")
                for src in d.get("sources", [])[:5]:
                    lines.append(f"    [{MUTED}]{src.get('date', '?')}: {src.get('slug', '?')}[/]")

        elif idea.idea_type == IdeaType.SUGGESTED_ACTION:
            if d.get("days_since"):
                lines.append(f"  [{AMBER}]Last Analysis[/]: {d['days_since']} days ago")
            if d.get("skill"):
                lines.append(f"  [{AMBER}]Skill Used[/]:    {d['skill']}")
            if d.get("suggested_tool"):
                lines.append(f"  [{AMBER}]Suggested[/]:     Run {d['suggested_tool'].upper()}")

        elif idea.idea_type == IdeaType.STALE_PLAYBOOK:
            if d.get("days_stale"):
                lines.append(f"  [{AMBER}]Days Since Update[/]: {d['days_stale']}")

        # Market data summary
        if idea.market_data:
            md = idea.market_data
            lines.append("")
            lines.append(f"  [{AMBER}]Market Data[/] (as of {md.get('updated', '?')})")
            if md.get("price"):
                chg = md.get("change_pct", 0)
                chg_color = GREEN if chg >= 0 else RED
                sign = "+" if chg >= 0 else ""
                lines.append(f"    Price:     ${md['price']:>12,.2f}  [{chg_color}]{sign}{chg:.2f}%[/]")
            if md.get("market_cap"):
                cap = md["market_cap"]
                if cap > 1e12:
                    lines.append(f"    Mkt Cap:   ${cap / 1e12:>12,.1f}T")
                elif cap > 1e9:
                    lines.append(f"    Mkt Cap:   ${cap / 1e9:>12,.1f}B")
                else:
                    lines.append(f"    Mkt Cap:   ${cap / 1e6:>12,.0f}M")

        # Actions
        if idea.actions:
            lines.append("")
            lines.append(f"  [{AMBER}]ACTIONS[/]")
            for i, action in enumerate(idea.actions[:4]):
                lines.append(f"    [{BRIGHT}][{i + 1}][/] {action['label']}")

        return "\n".join(lines)

    # ── Action handlers ──

    def action_idea_action(self, index: int) -> None:
        """Execute a numbered action from the current idea."""
        if not self._selected or index >= len(self._selected.actions):
            return
        action = self._selected.actions[index]
        action_type = action.get("type")

        if action_type == "wiki":
            target = action.get("target")
            if target and isinstance(target, (list, tuple)) and len(target) == 2:
                self.app.action_switch_screen("wiki")
                # Defer select_page until the screen has mounted
                self.set_timer(0.1, lambda: (
                    self.app.screen.select_page(target[0], target[1])
                    if hasattr(self.app.screen, "select_page") else None
                ))
        elif action_type == "tool":
            tool_key = action.get("target")
            if tool_key:
                self.app.action_switch_screen("tools")
                self.set_timer(0.1, lambda: (
                    self.app.screen.select_tool(tool_key)
                    if hasattr(self.app.screen, "select_tool") else None
                ))
        elif action_type == "screen":
            target = action.get("target")
            if target:
                self.app.action_switch_screen(target)

    def action_next_idea(self) -> None:
        filtered = self._get_filtered_ideas()
        if not filtered or not self._selected:
            return
        try:
            idx = filtered.index(self._selected)
            if idx < len(filtered) - 1:
                self._select_idea(filtered[idx + 1])
        except ValueError:
            if filtered:
                self._select_idea(filtered[0])

    def action_prev_idea(self) -> None:
        filtered = self._get_filtered_ideas()
        if not filtered or not self._selected:
            return
        try:
            idx = filtered.index(self._selected)
            if idx > 0:
                self._select_idea(filtered[idx - 1])
        except ValueError:
            if filtered:
                self._select_idea(filtered[0])

    def refresh_data(self) -> None:
        """Full refresh — re-scan wiki and re-fetch market data."""
        self.query_one("#idea-content", Static).update(
            f"[{MUTED}]Refreshing ideas...[/]"
        )
        self._load_ideas()
