# 9Router MCP Server

FastMCP server providing 35 tools for full management of a 9Router instance.

## Setup

```bash
cd mcp
pip install -e .
```

## Run

```bash
cd mcp
fastmcp run nine_router_mcp/server.py
```

## Configuration

| Variable | Default | Description |
|---|---|---|
| `NINE_ROUTER_URL` | `http://localhost:20128` | Base URL of running 9Router instance |

Assumes 9Router is running with `requireLogin` disabled.

## MCP Config

### Cursor (recommended for this repo)

Project file: **`.cursor/mcp.json`** (committed; merges with `~/.cursor/mcp.json`).
Uses `${workspaceFolder}` for the server script path and `PYTHONPATH`, because some Cursor builds do not apply `cwd` for user-scoped MCP servers (symptom: `File not found .../Users/<you>/nine_router_mcp/server.py`).

Requires `fastmcp` on your PATH and `pip install -e .` from `mcp/`.

### Generic `.mcp.json`

Add to your user or project `.mcp.json`:

```json
{
  "mcpServers": {
    "9router": {
      "command": "fastmcp",
      "args": ["run", "/path/to/9router-fork/mcp/nine_router_mcp/server.py"],
      "cwd": "/path/to/9router-fork/mcp",
      "env": {
        "NINE_ROUTER_URL": "http://localhost:20128",
        "PYTHONPATH": "/path/to/9router-fork/mcp"
      }
    }
  }
}
```

Override the base URL without editing the file: set `NINE_ROUTER_URL` in your environment and use `"NINE_ROUTER_URL": "${env:NINE_ROUTER_URL}"` in `mcp.json` (Cursor interpolation).

## Troubleshooting (Cursor)

| Log / symptom | Cause | Fix |
|---------------|--------|-----|
| `File not found: /Users/…/nine_router_mcp/server.py` (under home, no `…/mcp/…`) | `fastmcp` resolved a **relative** script path from `$HOME`; **`cwd` not applied** for some user MCP entries | Use **absolute** `args` (e.g. `${workspaceFolder}/mcp/nine_router_mcp/server.py`) and set **`PYTHONPATH`** to the `mcp/` directory — see **`.cursor/mcp.json`** in this repo |
| Duplicate `9router` in user + project config | Merge / naming (`user-9router`) confusion | Prefer **project-only** `.cursor/mcp.json`, or align both entries to the same absolute path + `PYTHONPATH` |

After changing `mcp.json`, **reload Cursor** or restart so MCP picks up the new config.
