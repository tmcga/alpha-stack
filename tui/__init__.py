"""Alpha Stack TUI — Bloomberg Terminal-inspired interface for finance."""

try:
    import textual  # noqa: F401
except ImportError:
    raise ImportError(
        "The Alpha Stack TUI requires textual. Install it with:\n"
        "  pip install textual\n"
        "Or run: ./setup-tui.sh"
    )
