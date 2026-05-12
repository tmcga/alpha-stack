"""Alpha Stack chat endpoint — BYOK Claude API with tool-use loop.

Users supply their own Anthropic API key via the X-Anthropic-Key header.
The server never persists the key; it builds a one-shot client per request.

Tools are auto-generated from the TOOLS registry — every calculator becomes
a Claude tool, so users can say "size a $28M loan at 6.25% with $1.8M NOI"
and Claude calls re_debt_sizing automatically.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

import anthropic
from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Ensure tools/ + tui/ on path (mirrors plugin/server/app.py)
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
for _p in (_ROOT, os.path.join(_ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from tui.registry import TOOLS, import_tool, parse_param  # noqa: E402

router = APIRouter()

# ── Tool schema generation ──────────────────────────────────────────────────

_TYPE_MAP = {
    "float": {"type": "number"},
    "int": {"type": "integer"},
    "str": {"type": "string"},
    "list[float]": {"type": "array", "items": {"type": "number"}},
    "list[list[float]]": {"type": "array", "items": {"type": "array", "items": {"type": "number"}}},
}


def _tool_schema(key: str, spec: dict) -> dict:
    """Convert a TOOLS registry entry into an Anthropic tool schema."""
    properties: dict[str, Any] = {}
    required: list[str] = []
    for p in spec["params"]:
        base = _TYPE_MAP.get(p["type"], {"type": "string"}).copy()
        desc = p["label"]
        if p.get("hint"):
            desc = f"{desc}. Example: {p['hint']}"
        if p.get("default") is not None and not p["required"]:
            desc = f"{desc}. Default: {p['default']}"
        base["description"] = desc
        properties[p["name"]] = base
        if p["required"]:
            required.append(p["name"])
    return {
        "name": f"alpha_{key}",
        "description": f"{spec['name']} — {spec['category']} calculator from Alpha Stack. Returns a JSON object with results.",
        "input_schema": {
            "type": "object",
            "properties": properties,
            "required": required,
        },
    }


def _build_tool_schemas() -> list[dict]:
    return [_tool_schema(k, v) for k, v in TOOLS.items()]


_TOOL_SCHEMAS = _build_tool_schemas()
_TOOL_KEY_BY_NAME = {f"alpha_{k}": k for k in TOOLS}


def _execute_tool(name: str, inputs: dict) -> dict:
    """Run a registry tool by Claude-facing name and return its result."""
    key = _TOOL_KEY_BY_NAME.get(name)
    if not key:
        return {"error": f"Unknown tool: {name}"}
    spec = TOOLS[key]
    fn = import_tool(key)
    kwargs = {}
    for p in spec["params"]:
        if p["name"] in inputs:
            val = inputs[p["name"]]
            # Claude may pass lists as strings if the model gets confused; coerce
            if isinstance(val, str) and p["type"] in ("list[float]", "list[list[float]]"):
                try:
                    val = parse_param(val, p["type"])
                except (ValueError, SyntaxError) as e:
                    return {"error": f"Invalid {p['label']}: {e}"}
            kwargs[p["name"]] = val
        elif p["required"]:
            return {"error": f"Missing required parameter: {p['label']}"}
    try:
        return fn(**kwargs)
    except Exception as e:  # noqa: BLE001
        return {"error": f"{type(e).__name__}: {e}"}


# ── System prompt ────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """You are Alpha Stack, an AI analyst for finance professionals.

You have access to 25 institutional-grade calculators covering valuation (DCF, LBO, WACC, IRR),
options (Black-Scholes, implied vol, convertibles), fixed income (bonds, Merton, Z-Score),
portfolio (Black-Litterman, Brinson, Kelly, Monte Carlo, risk), M&A (merger arb), market making,
real estate (cap rate, debt sizing, waterfall, development, NOI), and VC/lending (fund metrics,
loan amortization, depreciation).

When the user asks a quantitative question, call the relevant tool with the numbers they
provided. Don't ask for inputs that aren't required. Use sensible defaults when the user
hasn't specified an optional parameter.

When presenting results:
- Lead with the headline number (IRR, MOIC, price target, debt size, etc.)
- Show the key breakdown (returns attribution, sensitivity, risks)
- Flag what kills the thesis — the assumption most likely to be wrong
- Never invent financial data. If the user didn't give a number, ask for it.

Be terse. Investment professionals want answers, not paragraphs of preamble. Tables and
bullets over prose. When uncertain about a calculation choice (e.g. Gordon Growth vs Exit
Multiple terminal), pick one and note the trade-off rather than asking."""


# ── Request/response models ─────────────────────────────────────────────────


class ChatMessage(BaseModel):
    role: str
    content: Any  # str or list[ContentBlock]


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    model: str = "claude-opus-4-7"


# ── Endpoint ─────────────────────────────────────────────────────────────────


def _err_event(msg: str) -> str:
    return f"data: {json.dumps({'type': 'error', 'error': msg})}\n\n"


@router.post("/chat")
async def chat(
    req: ChatRequest,
    x_anthropic_key: str | None = Header(default=None, alias="X-Anthropic-Key"),
):
    """BYOK chat endpoint — streams SSE events.

    Event types emitted:
      - text_delta: partial assistant text
      - tool_use_start: { name, input } — Claude is about to call a tool
      - tool_result: { name, result } — calculator output
      - turn_end: { stop_reason, usage } — model finished or hit end of turn
      - error: { error }
    """
    if not x_anthropic_key:
        raise HTTPException(status_code=401, detail="Missing X-Anthropic-Key header (BYOK).")
    if not x_anthropic_key.startswith("sk-ant-"):
        raise HTTPException(status_code=400, detail="API key must start with 'sk-ant-'.")

    client = anthropic.Anthropic(api_key=x_anthropic_key)
    messages: list[dict] = [m.model_dump() for m in req.messages]

    def event_stream():
        try:
            # Tool-use loop — keep going until stop_reason == "end_turn"
            # See shared/tool-use-concepts.md (Anthropic skill) for the pattern
            for _ in range(8):  # safety cap on loop iterations
                with client.messages.stream(
                    model=req.model,
                    max_tokens=4096,
                    system=_SYSTEM_PROMPT,
                    tools=_TOOL_SCHEMAS,
                    messages=messages,
                ) as stream:
                    for event in stream:
                        if event.type == "content_block_start":
                            if event.content_block.type == "tool_use":
                                yield (
                                    "data: "
                                    + json.dumps({
                                        "type": "tool_use_start",
                                        "name": event.content_block.name,
                                    })
                                    + "\n\n"
                                )
                        elif event.type == "content_block_delta":
                            if event.delta.type == "text_delta":
                                yield (
                                    "data: "
                                    + json.dumps({"type": "text_delta", "text": event.delta.text})
                                    + "\n\n"
                                )
                    response = stream.get_final_message()

                # Append assistant message (preserves tool_use blocks)
                messages.append({"role": "assistant", "content": [b.model_dump() for b in response.content]})

                if response.stop_reason != "tool_use":
                    yield (
                        "data: "
                        + json.dumps({
                            "type": "turn_end",
                            "stop_reason": response.stop_reason,
                            "usage": {
                                "input_tokens": response.usage.input_tokens,
                                "output_tokens": response.usage.output_tokens,
                            },
                        })
                        + "\n\n"
                    )
                    return

                # Execute each tool the model requested
                tool_results = []
                for block in response.content:
                    if block.type != "tool_use":
                        continue
                    result = _execute_tool(block.name, block.input)
                    yield (
                        "data: "
                        + json.dumps({
                            "type": "tool_result",
                            "name": block.name,
                            "input": block.input,
                            "result": result,
                        })
                        + "\n\n"
                    )
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result, default=str),
                        "is_error": isinstance(result, dict) and "error" in result,
                    })

                messages.append({"role": "user", "content": tool_results})

            yield _err_event("Loop iteration cap reached (8). Try a more direct question.")
        except anthropic.AuthenticationError:
            yield _err_event("Invalid Anthropic API key. Check it at console.anthropic.com.")
        except anthropic.RateLimitError as e:
            yield _err_event(f"Rate limited by Anthropic: {e}")
        except anthropic.APIError as e:
            yield _err_event(f"Anthropic API error: {e}")
        except Exception as e:  # noqa: BLE001
            yield _err_event(f"{type(e).__name__}: {e}")

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/chat/models")
async def list_models():
    """Available models for the chat UI's selector."""
    return {
        "models": [
            {"id": "claude-opus-4-7", "name": "Opus 4.7", "tagline": "Most capable. Default."},
            {"id": "claude-sonnet-4-6", "name": "Sonnet 4.6", "tagline": "Balanced. Cheaper."},
            {"id": "claude-haiku-4-5", "name": "Haiku 4.5", "tagline": "Fast. Cheapest."},
        ]
    }
