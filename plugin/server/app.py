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


# ── Sensitivity endpoint ──────────────────────────────────────────────────


@app.post("/tools/{key}/sensitivity")
async def sensitivity_grid(key: str, body: dict):
    """Generate a 5x5 sensitivity grid for a tool by varying two parameters.

    Body: {
        base_params: {...},           # all required params at base case
        row_param: "wacc",            # name of the param varied across rows
        row_values: [0.08, 0.09, ...],
        col_param: "terminal_growth",
        col_values: [0.02, 0.025, ...],
        output_key: "price_per_share" # which top-level field to extract from result
    }
    """
    if key not in TOOLS:
        raise HTTPException(status_code=404, detail=f"Tool '{key}' not found")

    base_params = body.get("base_params", {})
    row_param = body.get("row_param")
    col_param = body.get("col_param")
    row_values = body.get("row_values", [])
    col_values = body.get("col_values", [])
    output_key = body.get("output_key")

    if not (row_param and col_param and row_values and col_values and output_key):
        raise HTTPException(status_code=422, detail="Missing row/col param, values, or output_key")
    if row_param == col_param:
        raise HTTPException(status_code=422, detail="row_param and col_param must differ")

    tool_spec = TOOLS[key]
    fn = import_tool(key)
    param_types = {p["name"]: p["type"] for p in tool_spec["params"]}

    def _coerce(val, name):
        t = param_types.get(name)
        if isinstance(val, str) and t in ("list[float]", "list[list[float]]"):
            return parse_param(val, t)
        return val

    # Pre-coerce list-type base params
    coerced_base = {k: _coerce(v, k) for k, v in base_params.items()}

    grid = []
    errors = []
    for r in row_values:
        row = []
        for c in col_values:
            kwargs = dict(coerced_base)
            kwargs[row_param] = r
            kwargs[col_param] = c
            try:
                result = fn(**kwargs)
                # Walk dotted output_key (e.g. "attribution.deleveraging")
                val = result
                for part in output_key.split("."):
                    if isinstance(val, dict) and part in val:
                        val = val[part]
                    else:
                        val = None
                        break
                row.append(val)
            except Exception as e:  # noqa: BLE001
                row.append(None)
                errors.append(f"r={r},c={c}: {type(e).__name__}: {e}")
        grid.append(row)

    return {
        "ok": True,
        "grid": grid,
        "row_param": row_param,
        "col_param": col_param,
        "row_values": row_values,
        "col_values": col_values,
        "output_key": output_key,
        "errors": errors[:5] if errors else [],
    }


# ── Templates list (web-friendly subset) ───────────────────────────────────


@app.get("/templates/web")
async def list_templates_web():
    """Return template starter inputs in a format the web app can consume."""
    from plugin.server.templates import TEMPLATES
    starters = []
    for key, t in TEMPLATES.items():
        # Pick the first tool and its input defaults
        if not t.get("tools") or not t.get("inputs"):
            continue
        tool_key = t["tools"][0]
        if tool_key not in TOOLS:
            continue
        # Map template input cells to {param: default}
        defaults = {c["param"]: c["default"] for c in t["inputs"]["cells"] if "param" in c and "default" in c}
        starters.append({
            "key": key,
            "name": t["name"],
            "description": t["description"],
            "tool_key": tool_key,
            "tool_name": TOOLS[tool_key]["name"],
            "defaults": defaults,
            "sensitivity": t.get("sensitivity"),
        })
    return {"starters": starters}


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
