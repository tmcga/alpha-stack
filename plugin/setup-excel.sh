#!/bin/bash
# Alpha Stack Excel Add-in installer
# Usage: ./plugin/setup-excel.sh

set -e

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║   Alpha Stack Excel Add-in Setup     ║"
echo "  ║   Finance Tools Inside Excel         ║"
echo "  ╚══════════════════════════════════════╝"
echo ""

# Check Python 3.10+
if ! command -v python3 &> /dev/null; then
    echo "  ✗ Python 3 not found. Install Python 3.10+ first."
    exit 1
fi
PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "  ✓ Python $PY_VERSION"

# Install dependencies
echo "  Installing FastAPI and Uvicorn..."
if command -v uv &> /dev/null; then
    uv pip install fastapi uvicorn 2>/dev/null || pip install fastapi uvicorn
else
    pip install fastapi uvicorn
fi
echo "  ✓ Dependencies installed"

# Verify import
if python3 -c "from fastapi import FastAPI" 2>/dev/null; then
    echo "  ✓ FastAPI verified"
else
    echo "  ✗ Failed to import FastAPI"
    exit 1
fi

# Start server
echo ""
echo "  Starting Alpha Stack API server..."
cd "$REPO_DIR"
uvicorn plugin.server.app:app --host 127.0.0.1 --port 8765 &
SERVER_PID=$!
sleep 2

# Health check
if curl -s http://127.0.0.1:8765/health | grep -q '"ok"'; then
    echo "  ✓ Server running on http://localhost:8765"
else
    echo "  ✗ Server failed to start"
    kill $SERVER_PID 2>/dev/null
    exit 1
fi

echo ""
echo "  ┌──────────────────────────────────────┐"
echo "  │         Next Steps                   │"
echo "  │                                      │"
echo "  │  1. Open Excel                       │"
echo "  │  2. Insert → Get Add-ins             │"
echo "  │  3. Upload My Add-in                 │"
echo "  │  4. Select: plugin/addin/manifest.xml│"
echo "  │  5. Click 'Alpha Stack' in ribbon    │"
echo "  │                                      │"
echo "  │  Server PID: $SERVER_PID                │"
echo "  │  Stop: kill $SERVER_PID                 │"
echo "  └──────────────────────────────────────┘"
echo ""
echo "  The add-in sidebar will connect to:"
echo "  http://localhost:8765/addin/taskpane.html"
echo ""
