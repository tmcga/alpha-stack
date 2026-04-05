"""Wiki Browser — browse and search the personal knowledge base."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Input, Markdown, Static, Tree

from tui.theme import AMBER, MUTED
from tui.widgets.ticker_bar import TickerBar


class WikiBrowserScreen(Screen):
    """Browse and search the wiki knowledge base."""

    BINDINGS = [
        ("s", "focus_search", "Search"),
    ]

    def compose(self) -> ComposeResult:
        yield Static(
            f"[bold {AMBER}] WIKI BROWSER[/]",
            id="header",
        )
        yield Static(
            f"[{AMBER}] F1:HOME  F2:WIKI  F3:TOOLS  F4:IDEAS"
            f"{'':>24}[s]earch  Ctrl+Q:Quit[/]",
            id="fn-bar",
        )

        with Horizontal(id="wiki-browser"):
            with Vertical(id="wiki-sidebar"):
                tree = Tree("Wiki", id="wiki-tree")
                tree.show_root = False
                yield tree

            with Vertical(id="wiki-content"):
                yield Markdown(
                    "*Select a page from the sidebar to view it here.*",
                    id="wiki-viewer",
                )

        with Vertical(id="command-bar"):
            yield Static(f"[bold {AMBER}]SEARCH>[/] ", classes="cmd-label")
            yield Input(placeholder="Search wiki pages...", id="wiki-search")

        yield TickerBar()

    def on_mount(self) -> None:
        self._load_tree()

    def _load_tree(self, filter_text: str | None = None) -> None:
        """Populate the wiki tree from wiki_list_pages."""
        tree = self.query_one("#wiki-tree", Tree)
        tree.clear()
        try:
            from wiki import wiki_list_pages, wiki_search

            if filter_text:
                result = wiki_search(filter_text)
                matches = {(m["category"], m["slug"]) for m in result.get("matches", [])}
            else:
                matches = None

            pages = wiki_list_pages()
            # Group by category
            by_cat: dict[str, list] = {}
            for p in pages.get("pages", []):
                cat = p["category"]
                if cat == "raw":
                    continue
                if matches is not None and (cat, p["slug"]) not in matches:
                    continue
                by_cat.setdefault(cat, []).append(p)

            if not by_cat:
                if filter_text:
                    tree.root.add_leaf(f"[{MUTED}]No results for '{filter_text}'[/]")
                else:
                    tree.root.add_leaf(f"[{MUTED}]Wiki empty. Run /wiki init[/]")
                return

            for cat in ("entities", "playbooks", "journal"):
                if cat not in by_cat:
                    continue
                branch = tree.root.add(f"[{AMBER}]{cat.upper()}[/]", expand=True)
                for p in by_cat[cat]:
                    branch.add_leaf(p["slug"], data={"category": cat, "slug": p["slug"]})

        except Exception as e:
            tree.root.add_leaf(f"[{MUTED}]Error: {e}[/]")

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Load a wiki page when selected."""
        if not event.node.data or not isinstance(event.node.data, dict):
            return
        cat = event.node.data.get("category")
        slug = event.node.data.get("slug")
        if cat and slug:
            self.select_page(cat, slug)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "wiki-search":
            query = event.value.strip()
            self._load_tree(filter_text=query if query else None)

    def action_focus_search(self) -> None:
        self.query_one("#wiki-search", Input).focus()

    def select_page(self, category: str, slug: str) -> None:
        """Programmatically select and display a wiki page (for cross-screen nav)."""
        try:
            from wiki import wiki_read_page
            result = wiki_read_page(category, slug)
            viewer = self.query_one("#wiki-viewer", Markdown)
            if "error" in result:
                viewer.update(f"*{result['error']}*")
            else:
                viewer.update(result["content"])
        except Exception as e:
            self.query_one("#wiki-viewer", Markdown).update(f"*Error: {e}*")
