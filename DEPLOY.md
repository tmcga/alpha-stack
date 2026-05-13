# Deploying Alpha Stack to Vercel

This deploys the web app (landing page + 25-tool runner) to Vercel as Python serverless functions.

## What gets deployed

| Path | Source | What it is |
|------|--------|-----------|
| `/` | `public/index.html` | Landing page with tool catalog |
| `/app` | `public/app.html` | Tool runner UI |
| `/styles.css` `/app.js` | `public/` | Static assets |
| `/api/health` | `app.py` → `plugin/server/app.py` | Health check |
| `/api/tools` | `app.py` | Tool registry (categories + params) |
| `/api/tools/{key}/run` | `app.py` | Execute a tool with JSON params |

Everything else (TUI, MCP server, Excel add-in, Claude Code skills) is **not** part of the Vercel deploy. They remain installable locally for power users.

## What's NOT on Vercel

- **TUI** ([tui/](tui/)) — terminal-only, ships as a separate install
- **MCP server** ([mcp_server.py](mcp_server.py)) — Claude Desktop only
- **Excel add-in** ([plugin/addin/](plugin/addin/)) — requires Office sideloading; the FastAPI server it depends on is now also exposed via `/api/*` on Vercel, so you could repoint the manifest at your Vercel URL if you want to host the Excel add-in too
- **Wiki / sessions persistence** — Vercel's filesystem is ephemeral (`/tmp` only). State written during a function invocation will not survive between requests. The endpoints work; they just don't persist. Use locally for the real wiki.

## One-time deploy

```bash
# 1. Install the Vercel CLI
npm i -g vercel

# 2. From the repo root
cd ~/alpha-prompts
vercel              # follow prompts; link or create a new project
vercel --prod       # deploy to production
```

Vercel auto-detects:
- `requirements.txt` → installs FastAPI for the Python runtime
- `app.py` → mounts as a serverless function
- `public/` → serves as static files
- `vercel.json` → routing + headers

## Local development

```bash
source .venv/bin/activate     # or create a venv with fastapi + uvicorn
uvicorn app:app --reload --port 8765
# visit http://127.0.0.1:8765
```

`app.py` also mounts `public/` as static for local dev, so the full app works under uvicorn without `vercel dev`.

## Environment variables

Set in the Vercel dashboard under **Settings → Environment Variables**:

| Var | Default | Notes |
|-----|---------|-------|
| `ALPHA_STACK_STATE_DIR` | `/tmp/alpha-stack/sessions` | Set by `app.py`; safe to leave default |
| `ALPHA_STACK_WIKI_DIR` | `/tmp/alpha-stack/wiki` | Set by `app.py`; safe to leave default |

Neither is required, and neither persists. If you want a real persistence layer for sessions/wiki, swap in Vercel KV, Postgres, or Blob Storage — the read/write surface is small (see [tools/state.py](tools/state.py) and [tools/wiki.py](tools/wiki.py)).

## Custom domain

`vercel domains add alpha-stack.example.com` in the CLI, or attach a domain in the dashboard. Vercel handles HTTPS automatically.

## Caveats

- **Cold starts**: First request to `/api/*` after idle takes ~1.5s. Subsequent requests are <100ms.
- **Function size limit**: 250MB unzipped. Current deploy is ~10MB.
- **Function timeout**: Set to 30s in [vercel.json](vercel.json). Monte Carlo at 100k+ sims may need more.
- **No persistence**: As above. Build on KV/Postgres if you need it.

## Smoke test the deploy

```bash
URL=https://your-deployment.vercel.app

curl -s $URL/api/health
# → {"status":"ok","tools":25,"version":"1.0.0"}

curl -s $URL/api/tools | jq '.categories'
# → ["Valuation","Options","Fixed Income","Portfolio","M&A / Trading","Real Estate","VC / Lending"]

curl -s -X POST $URL/api/tools/lbo/run \
  -H "Content-Type: application/json" \
  -d '{"ebitda":100,"entry_multiple":10,"exit_multiple":11,"leverage":5,"interest_rate":0.06,"ebitda_growth":0.08,"years":5}' \
  | jq '.result.irr'
# → 0.216 (21.6% IRR)
```
