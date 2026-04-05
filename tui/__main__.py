"""Entry point: python -m tui"""

import os
import sys

# Add tools/ to path so we can import tool functions directly
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from tui.app import AlphaStackApp  # noqa: E402

if __name__ == "__main__":
    app = AlphaStackApp()
    app.run()
