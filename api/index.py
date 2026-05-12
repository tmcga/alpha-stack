"""Vercel Python serverless entry point.

Wraps the existing FastAPI app so it's reachable at /api/*.
The base app's routes (e.g. /health, /tools) become /api/health, /api/tools.
"""

import os
import sys

# Make project root importable
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "tools"))

# Default ephemeral storage on Vercel
os.environ.setdefault("ALPHA_STACK_STATE_DIR", "/tmp/alpha-stack/sessions")
os.environ.setdefault("ALPHA_STACK_WIKI_DIR", "/tmp/alpha-stack/wiki")

from fastapi import FastAPI  # noqa: E402
from fastapi.responses import FileResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

from plugin.server.app import app as base_app  # noqa: E402

app = FastAPI(title="Alpha Stack on Vercel")
app.mount("/api", base_app)

# Serve the static frontend (for local dev — Vercel handles this via public/ in production)
_PUBLIC_DIR = os.path.join(_ROOT, "public")

# Pretty URL for the app — matches Vercel's cleanUrls behavior locally
@app.get("/app")
async def app_page():
    return FileResponse(os.path.join(_PUBLIC_DIR, "app.html"))


if os.path.isdir(_PUBLIC_DIR):
    app.mount("/", StaticFiles(directory=_PUBLIC_DIR, html=True), name="public")
