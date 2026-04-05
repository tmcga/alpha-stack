"""Alpha Stack API Server — wraps all finance tools as REST endpoints for the Excel Add-in.

Run: uvicorn plugin.server.app:app --host 127.0.0.1 --port 8765
"""

import importlib
import json
import os
import sys
import traceback

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

# Add tools/ and tui/ to sys.path (same pattern as mcp_server.py line 15)
_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(_ROOT, "tools"))
sys.path.insert(0, _ROOT)

from tui.registry import TOOLS, CATEGORIES, get_tools_by_category, import_tool, parse_param  # noqa: E402

app = FastAPI(
    title="Alpha Stack API",
    description="Finance tools for the Excel Add-in",
    version="1.0.0",
)

# CORS — allow Office Add-in origins (sideloaded add-ins send Origin: null)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the add-in static files
_ADDIN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "addin")
if os.path.isdir(_ADDIN_DIR):
    app.mount("/addin", StaticFiles(directory=_ADDIN_DIR, html=True), name="addin")


def _safe_call(fn, **kwargs) -> dict:
    """Execute a tool function with error handling."""
    try:
        result = fn(**kwargs)
        return {"ok": True, "result": result}
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


# ── Tool endpoints ────────────────────────────────────────────────────────


@app.get("/health")
async def health():
    return {"status": "ok", "tools": len(TOOLS), "version": "1.0.0"}


@app.get("/tools")
async def list_tools():
    """List all tools grouped by category with full param metadata."""
    grouped = get_tools_by_category()
    return {"categories": CATEGORIES, "tools": grouped}


@app.get("/tools/{key}")
async def get_tool(key: str):
    """Get a single tool's metadata."""
    if key not in TOOLS:
        raise HTTPException(status_code=404, detail=f"Tool '{key}' not found")
    return TOOLS[key]


@app.post("/tools/{key}/run")
async def run_tool(key: str, params: dict):
    """Execute a tool with the given parameters."""
    if key not in TOOLS:
        raise HTTPException(status_code=404, detail=f"Tool '{key}' not found")

    tool_spec = TOOLS[key]
    fn = import_tool(key)

    # Build kwargs from params, validating against the registry
    kwargs = {}
    for param in tool_spec["params"]:
        name = param["name"]
        if name in params:
            val = params[name]
            # JSON already provides correct types for most cases,
            # but strings need parsing for list/complex types
            if isinstance(val, str) and param["type"] in ("list[float]", "list[list[float]]"):
                try:
                    val = parse_param(val, param["type"])
                except (ValueError, SyntaxError) as e:
                    return JSONResponse(
                        status_code=422,
                        content={"ok": False, "error": f"Invalid '{param['label']}': {e}"},
                    )
            kwargs[name] = val
        elif param["required"]:
            return JSONResponse(
                status_code=422,
                content={"ok": False, "error": f"Missing required parameter: {param['label']}"},
            )

    return _safe_call(fn, **kwargs)


# ── Session endpoints ─────────────────────────────────────────────────────


@app.get("/sessions")
async def list_sessions():
    from state import list_sessions
    return list_sessions()


@app.get("/sessions/{name}")
async def load_session(name: str):
    from state import load_session
    result = load_session(name)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@app.post("/sessions/{name}")
async def save_session(name: str, body: dict):
    from state import save_session
    data = body.get("data", {})
    tags = body.get("tags", [])
    return save_session(name, data, tags)


@app.delete("/sessions/{name}")
async def delete_session(name: str):
    from state import delete_session
    result = delete_session(name)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


# ── Wiki endpoints ────────────────────────────────────────────────────────


@app.get("/wiki/status")
async def wiki_status():
    from wiki import wiki_status
    return wiki_status()


@app.get("/wiki/search")
async def wiki_search(q: str, category: str | None = None):
    from wiki import wiki_search
    return wiki_search(q, category)


@app.get("/wiki/pages")
async def wiki_list(category: str | None = None):
    from wiki import wiki_list_pages
    return wiki_list_pages(category)


@app.get("/wiki/pages/{category}/{slug}")
async def wiki_read(category: str, slug: str):
    from wiki import wiki_read_page
    result = wiki_read_page(category, slug)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


# ── Template endpoints ────────────────────────────────────────────────────


@app.get("/templates")
async def list_templates():
    from plugin.server.templates import TEMPLATES
    return {
        "templates": [
            {"key": k, "name": v["name"], "description": v["description"],
             "sheets": v["sheets"], "tools": v["tools"]}
            for k, v in TEMPLATES.items()
        ]
    }


@app.get("/templates/{key}")
async def get_template(key: str):
    from plugin.server.templates import TEMPLATES
    if key not in TEMPLATES:
        raise HTTPException(status_code=404, detail=f"Template '{key}' not found")
    return TEMPLATES[key]
