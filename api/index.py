"""Vercel Python serverless entry point.

Wraps the existing FastAPI app so it's reachable at /api/*.
The base app's routes (e.g. /health, /tools) become /api/health, /api/tools.

Heavy imports are wrapped so that if they fail (missing sibling dirs,
missing deps), /api/__diag still responds with what went wrong.
Route order matters — /api/__diag is registered BEFORE the /api mount
so it takes precedence over the mounted sub-app.
"""

import os
import sys
import traceback

# Make project root importable. On Vercel, __file__ resolves under /var/task/api/,
# so _ROOT = /var/task. tools/, plugin/, tui/ get bundled via vercel.json
# `includeFiles`.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "tools"))

# Ephemeral storage on Vercel — read-only filesystem except /tmp
os.environ.setdefault("ALPHA_STACK_STATE_DIR", "/tmp/alpha-stack/sessions")
os.environ.setdefault("ALPHA_STACK_WIKI_DIR", "/tmp/alpha-stack/wiki")

from fastapi import FastAPI  # noqa: E402
from fastapi.responses import FileResponse, JSONResponse  # noqa: E402

app = FastAPI(title="Alpha Stack on Vercel")

# Try to load the heavy app; capture any import error for /api/__diag.
_IMPORT_ERROR: str | None = None
_BASE_APP = None
try:
    from plugin.server.app import app as _base_app  # noqa: E402
    from plugin.server.chat import router as _chat_router  # noqa: E402

    _base_app.include_router(_chat_router)
    _BASE_APP = _base_app
except Exception:  # noqa: BLE001
    _IMPORT_ERROR = traceback.format_exc()


# ── Diagnostic — registered BEFORE the mount so it's always reachable ──
@app.get("/api/__diag")
async def diagnostic():
    return JSONResponse({
        "ok": _BASE_APP is not None,
        "import_error": _IMPORT_ERROR,
        "root": _ROOT,
        "sys_path_head": sys.path[:5],
        "root_listing": sorted(os.listdir(_ROOT))[:30] if os.path.isdir(_ROOT) else None,
        "tools_exists": os.path.isdir(os.path.join(_ROOT, "tools")),
        "plugin_exists": os.path.isdir(os.path.join(_ROOT, "plugin")),
        "plugin_server_exists": os.path.isdir(os.path.join(_ROOT, "plugin", "server")),
        "tui_exists": os.path.isdir(os.path.join(_ROOT, "tui")),
        "public_exists": os.path.isdir(os.path.join(_ROOT, "public")),
        "python": sys.version,
    })


# Mount the real app under /api if it loaded
if _BASE_APP is not None:
    app.mount("/api", _BASE_APP)


# ── Local-dev only routes (Vercel handles /, /app, /chat via static + rewrites) ──
_PUBLIC_DIR = os.path.join(_ROOT, "public")


@app.get("/app")
async def app_page():
    p = os.path.join(_PUBLIC_DIR, "app.html")
    return FileResponse(p) if os.path.isfile(p) else JSONResponse({"error": "app.html missing"}, status_code=404)


@app.get("/chat")
async def chat_page():
    p = os.path.join(_PUBLIC_DIR, "chat.html")
    return FileResponse(p) if os.path.isfile(p) else JSONResponse({"error": "chat.html missing"}, status_code=404)


if os.path.isdir(_PUBLIC_DIR):
    from fastapi.staticfiles import StaticFiles  # noqa: E402

    app.mount("/", StaticFiles(directory=_PUBLIC_DIR, html=True), name="public")
