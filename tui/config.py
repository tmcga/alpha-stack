"""TUI configuration loader — reads ~/.alpha-stack/tui.toml."""

import os

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".alpha-stack", "tui.toml")

# Defaults
DEFAULTS = {
    "refresh_interval": 300,
    "default_screen": "dashboard",
    "fred_series": ["DGS10", "DGS2", "FEDFUNDS", "VIXCLS", "UNRATE", "BAAFFM"],
    "auto_refresh": True,
}


def load_config() -> dict:
    """Load config from TOML file, falling back to defaults."""
    config = dict(DEFAULTS)
    if not os.path.exists(CONFIG_PATH):
        return config
    try:
        # Python 3.11+ has tomllib; fall back to manual parsing for 3.10
        try:
            import tomllib
            with open(CONFIG_PATH, "rb") as f:
                user = tomllib.load(f)
        except ImportError:
            # Minimal TOML-like parsing for 3.10
            user = _parse_simple_toml(CONFIG_PATH)
        # Merge sections
        for section in ("general", "market_data"):
            if section in user:
                config.update(user[section])
    except Exception:
        pass
    return config


def _parse_simple_toml(path: str) -> dict:
    """Parse a flat TOML file (no nested tables). Good enough for config."""
    result = {}
    current_section = {}
    current_name = None
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("["):
                if current_name:
                    result[current_name] = current_section
                current_name = line.strip("[]").strip()
                current_section = {}
            elif "=" in line:
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if val.lower() in ("true", "false"):
                    current_section[key] = val.lower() == "true"
                elif val.startswith("["):
                    items = val.strip("[]").split(",")
                    current_section[key] = [i.strip().strip('"').strip("'") for i in items if i.strip()]
                else:
                    try:
                        current_section[key] = int(val)
                    except ValueError:
                        try:
                            current_section[key] = float(val)
                        except ValueError:
                            current_section[key] = val
    if current_name:
        result[current_name] = current_section
    return result
