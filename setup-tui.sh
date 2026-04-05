#!/bin/bash
# Alpha Stack TUI installer — Bloomberg Terminal interface
# Usage: ./setup-tui.sh

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║      Alpha Stack TUI Installer       ║"
echo "  ║   Bloomberg Terminal for Finance AI   ║"
echo "  ╚══════════════════════════════════════╝"
echo ""

# Check Python 3.10+
if ! command -v python3 &> /dev/null; then
    echo "  ✗ Python 3 not found. Install Python 3.10+ first."
    exit 1
fi

PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "  ✓ Python $PY_VERSION"

# Install textual
echo "  Installing textual..."
if command -v uv &> /dev/null; then
    uv pip install textual 2>/dev/null || pip install textual
else
    pip install textual
fi
echo "  ✓ textual installed"

# Verify import
if python3 -c "import textual" 2>/dev/null; then
    echo "  ✓ Import verified"
else
    echo "  ✗ Failed to import textual"
    exit 1
fi

echo ""
echo "  Ready! Launch with:"
echo "    cd $REPO_DIR && python -m tui"
echo ""
