# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

9Router is a local AI routing gateway and dashboard. It acts as an OpenAI-compatible proxy (`/v1/*`) that routes traffic across multiple upstream AI providers with format translation, tiered fallback, OAuth token refresh, and usage tracking. The internal package name is `9router-app` (private).

## Development Commands

```bash
# Development (Next.js dev server on port 20128)
cp .env.example .env
npm install
PORT=20128 NEXT_PUBLIC_BASE_URL=http://localhost:20128 npm run dev

# Production build and start
npm run build
PORT=20128 HOSTNAME=0.0.0.0 NEXT_PUBLIC_BASE_URL=http://localhost:20128 npm run start

# Bun variants
npm run dev:bun
npm run build:bun
npm run start:bun
```

Default URLs: Dashboard at `http://localhost:20128/dashboard`, API at `http://localhost:20128/v1`.

## Running Tests

Tests live in `tests/` and use Vitest installed separately (not hoisted from root due to Next.js workspace):

```bash
# Install vitest once
cd /tmp && npm install vitest

# Run all tests (from tests/ directory)
cd tests/
NODE_PATH=/tmp/node_modules /tmp/node_modules/.bin/vitest run --reporter=verbose --config ./vitest.config.js

# Or use the package script
cd tests/ && npm test
```

## Architecture

### Request Flow for `/v1/chat/completions`

```
Client → /v1/chat/completions (next.config.mjs rewrites to /api/v1/...)
  → src/sse/handlers/chat.js       (parse model, handle combo iteration)
  → open-sse/handlers/chatCore.js  (detect format, translate request, dispatch executor)
  → open-sse/executors/<provider>  (provider-specific HTTP, streaming, token refresh)
  → open-sse/translator/*          (translate response back to client format)
  → src/lib/usageDb.js             (persist usage + logs)
```

### Two Key Directories

**`src/`** — Next.js app with dashboard UI and management APIs:
- `src/app/api/v1/*` — OpenAI-compatible endpoints (`chat/completions`, `messages`, `models`, `responses`, `embeddings`)
- `src/app/api/*` — Management APIs (providers, OAuth, keys, combos, aliases, usage, sync)
- `src/sse/handlers/chat.js` — Entry point for chat requests; handles combo fallback loop and account selection
- `src/lib/localDb.js` — Primary state DB (`${DATA_DIR}/db.json`) for providers, combos, keys, settings
- `src/lib/usageDb.js` — Usage/log DB (`~/.9router/usage.json`, `~/.9router/log.txt`) — **does not follow DATA_DIR**

**`open-sse/`** — Provider execution core (framework-agnostic):
- `open-sse/handlers/chatCore.js` — Translation, executor dispatch, 401/403 retry with token refresh
- `open-sse/executors/` — Per-provider executors (`antigravity`, `gemini-cli`, `github`, `kiro`, `codex`, `cursor`, `default`)
- `open-sse/translator/` — Format detection and conversion between `openai`, `openai-responses`, `claude`, `gemini` formats
- `open-sse/services/accountFallback.js` — Account cooldown and fallback decisions based on status codes/error heuristics
- `open-sse/utils/proxyFetch.js` — Patches `globalThis.fetch` with env-proxy support and MITM DNS bypass for Google Cloud APIs

### Model Naming Convention

Models use `<prefix>/<model-id>` format, e.g.:
- `cc/claude-opus-4-6` — Claude Code subscription
- `glm/glm-4.7` — GLM API key provider
- `if/kimi-k2-thinking` — iFlow free provider

Combo names are custom strings that expand to a sequence of models with automatic fallback.

### Provider Types

- **OAuth providers**: Claude Code (`cc`), Codex (`cx`), Gemini CLI (`gc`), iFlow (`if`), Qwen (`qw`), Kiro (`kr`), GitHub (`gh`), Cursor, Antigravity
- **API key providers**: GLM, MiniMax, Kimi, OpenAI, Anthropic, OpenRouter, and 30+ others
- **Compatible nodes**: Custom OpenAI/Anthropic-compatible endpoints managed via `src/app/api/provider-nodes`

### URL Routing

`next.config.mjs` rewrites `/v1/*` → `/api/v1/*`. The `/codex/*` path routes to the Responses API endpoint.

### Storage

| File | Contents | Env Control |
|------|----------|-------------|
| `${DATA_DIR}/db.json` | providers, combos, keys, aliases, settings | `DATA_DIR` (default `~/.9router`) |
| `~/.9router/usage.json` | token usage history | hardcoded path |
| `~/.9router/log.txt` | request status log | hardcoded path |
| `<repo>/logs/` | full request/response debug logs | `ENABLE_REQUEST_LOGS=true` |

### Key Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `JWT_SECRET` | `9router-default-secret-change-me` | Dashboard auth cookie signing |
| `INITIAL_PASSWORD` | `123456` | First-login password |
| `DATA_DIR` | `~/.9router` | Main DB location |
| `API_KEY_SECRET` | `endpoint-proxy-api-key-secret` | HMAC for generated API keys |
| `MACHINE_ID_SALT` | `endpoint-proxy-salt` | Stable machine ID hashing |
| `ENABLE_REQUEST_LOGS` | `false` | Full request/response logging under `logs/` |
| `REQUIRE_API_KEY` | `false` | Enforce Bearer auth on `/v1/*` (recommended for public deploys) |
| `BASE_URL` | `http://localhost:20128` | Server-side URL for cloud sync jobs (prefer over `NEXT_PUBLIC_BASE_URL`) |

### Tech Stack

- **Framework**: Next.js 16 (`output: "standalone"`) with webpack (not Turbopack)
- **UI**: React 19 + Tailwind CSS 4 + Recharts + @xyflow/react
- **DB**: LowDB 7 (JSON file) + better-sqlite3
- **Streaming**: SSE via WHATWG ReadableStream
- **Auth**: JWT (jose) + bcryptjs + OAuth 2.0 PKCE
- **HTTP**: undici (with ProxyAgent for proxy support)
- **Node.js**: 20+
