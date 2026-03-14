# 9Router MCP Server — Design Spec
**Date:** 2026-03-14
**Status:** Approved

---

## Overview

A FastMCP server providing full management and control of a running 9Router instance. Exposes 35 tools across 7 domain modules, communicating with 9Router's management REST API (`/api/*`). Intended for use by AI agents and Claude Code sessions that need to inspect, configure, or monitor a local or remote 9Router gateway.

---

## Location

`mcp/` subdirectory inside the `9router-fork` repo. Package name: `nine_router_mcp` (avoids collision with stdlib `mcp` module).

---

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `NINE_ROUTER_URL` | `http://localhost:20128` | Base URL of the running 9Router instance |

No authentication — assumes 9Router is running with `requireLogin` disabled (local use).

If 9Router has login enabled, all management API calls will return 401. The error handler in `client.py` must surface: `"9Router returned 401. Login may be required — check requireLogin in settings or disable it."`

---

## Project Structure

```
mcp/
├── server.py              # FastMCP entry point; imports and registers all tool modules
├── client.py              # Shared httpx.AsyncClient; NINE_ROUTER_URL config
├── tools/
│   ├── providers.py       # Provider connection + node management
│   ├── combos.py          # Combo (fallback chain) management
│   ├── keys.py            # API key management
│   ├── models.py          # Model listing and alias management
│   ├── usage.py           # Usage stats, logs, history
│   ├── settings.py        # Global settings (non-password fields only)
│   └── system.py          # Proxy pools, tunnel, version
├── pyproject.toml
└── README.md
```

---

## Shared Infrastructure (`client.py`)

- Single `httpx.AsyncClient` instance configured with `NINE_ROUTER_URL` and 30s timeout
- All tool modules import `client` from this module — no URL logic in tool files
- Connection errors caught and returned as actionable messages: `"Cannot reach 9Router at {url}. Is it running?"`
- 401 responses return: `"9Router returned 401. Login may be required — check requireLogin in settings or disable it."`

---

## Tool Inventory

### `tools/providers.py` — 10 tools

| Tool | Method | Endpoint |
|---|---|---|
| `list_providers` | GET | `/api/providers` |
| `get_provider` | GET | `/api/providers/{id}` |
| `create_provider` | POST | `/api/providers` |
| `update_provider` | PUT | `/api/providers/{id}` |
| `delete_provider` | DELETE | `/api/providers/{id}` |
| `test_provider` | POST | `/api/providers/{id}/test` |
| `list_provider_nodes` | GET | `/api/provider-nodes` |
| `create_provider_node` | POST | `/api/provider-nodes` |
| `update_provider_node` | PUT | `/api/provider-nodes/{id}` |
| `delete_provider_node` | DELETE | `/api/provider-nodes/{id}` |

### `tools/combos.py` — 5 tools

| Tool | Method | Endpoint |
|---|---|---|
| `list_combos` | GET | `/api/combos` |
| `get_combo` | GET | `/api/combos/{id}` |
| `create_combo` | POST | `/api/combos` |
| `update_combo` | PUT | `/api/combos/{id}` |
| `delete_combo` | DELETE | `/api/combos/{id}` |

### `tools/keys.py` — 3 tools

| Tool | Method | Endpoint |
|---|---|---|
| `list_api_keys` | GET | `/api/keys` |
| `create_api_key` | POST | `/api/keys` |
| `delete_api_key` | DELETE | `/api/keys/{id}` |

### `tools/models.py` — 3 tools

| Tool | Method | Endpoint |
|---|---|---|
| `list_models` | GET | `/api/models` |
| `set_model_alias` | PUT | `/api/models/alias` |
| `delete_model_alias` | DELETE | `/api/models/alias` |

### `tools/usage.py` — 4 tools

| Tool | Method | Endpoint | Notes |
|---|---|---|---|
| `get_usage_stats` | GET | `/api/usage/stats` | `period` param: `24h`, `7d`, `30d`, `60d`, `all` (default `7d`) |
| `get_usage_logs` | GET | `/api/usage/logs` | Returns last 200 entries |
| `get_usage_history` | GET | `/api/usage/history` | Chart data over time |
| `get_request_details` | GET | `/api/usage/request-details` | Full detail for a specific request ID |

### `tools/settings.py` — 2 tools

| Tool | Method | Endpoint | Notes |
|---|---|---|---|
| `get_settings` | GET | `/api/settings` | Password hash excluded from response |
| `update_settings` | PATCH | `/api/settings` | **Password fields (`newPassword`, `currentPassword`) are explicitly excluded** — agents must not change dashboard auth |

### `tools/system.py` — 8 tools

| Tool | Method | Endpoint | Notes |
|---|---|---|---|
| `get_version` | GET | `/api/version` | Returns currentVersion, latestVersion, hasUpdate |
| `list_proxy_pools` | GET | `/api/proxy-pools` | |
| `get_proxy_pool` | GET | `/api/proxy-pools/{id}` | |
| `create_proxy_pool` | POST | `/api/proxy-pools` | |
| `update_proxy_pool` | PUT | `/api/proxy-pools/{id}` | |
| `delete_proxy_pool` | DELETE | `/api/proxy-pools/{id}` | Returns 409 if pool is in use by providers |
| `get_tunnel_status` | GET | `/api/tunnel/status` | |
| `set_tunnel` | POST | `/api/tunnel/enable` or `/api/tunnel/disable` | Takes `enabled: bool` param |

**Total: 35 tools**

---

## Response Design

- **Read operations** (list/get): concise Markdown — tables for lists, key-value blocks for single items. Omit sensitive fields (tokens, apiKey, accessToken, refreshToken).
- **Write operations** (create/update/delete): short confirmation with key changed fields.
- **Error responses**: always include what went wrong + what to do next.

### Error Message Patterns

| HTTP Status | Message Pattern |
|---|---|
| 400 | Surface 9Router's validation message verbatim |
| 401 | `"9Router returned 401. Login may be required — check requireLogin in settings or disable it."` |
| 404 | `"{resource} '{id}' not found. Use list_{resource}s to see valid IDs."` |
| 409 | `"Cannot delete — resource is still in use. Remove it from bound providers first."` |
| 500 | `"9Router returned an internal error. Check server logs."` |
| Connection refused | `"Cannot reach 9Router at {NINE_ROUTER_URL}. Is it running?"` |

---

## pyproject.toml Dependencies

```toml
[project]
name = "nine-router-mcp"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastmcp>=2.0",
    "httpx>=0.27",
]
```

---

## Running the Server

```bash
# Install dependencies
cd mcp && pip install -e .

# Run via fastmcp CLI (recommended)
fastmcp run server.py

# Or via uv
uv run fastmcp run server.py
```

## MCP Config (`.mcp.json` snippet)

```json
{
  "mcpServers": {
    "9router": {
      "command": "fastmcp",
      "args": ["run", "server.py"],
      "cwd": "/path/to/9router-fork/mcp",
      "env": {
        "NINE_ROUTER_URL": "http://localhost:20128"
      }
    }
  }
}
```

---

## Out of Scope

- OAuth flows (require browser redirects — not suitable for MCP tools)
- Password management (`newPassword`/`currentPassword` excluded from `update_settings`)
- Translator/console-log streaming endpoints
- Cloud sync endpoints
- CLI tool settings (antigravity, claude-settings, etc.)
- Shutdown endpoint (too destructive for agent use)
