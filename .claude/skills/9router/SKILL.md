---
name: 9router
description: >-
  9Router gateway and FastMCP tooling — use when configuring or debugging the
  nine_router_mcp server, Cursor MCP (.cursor/mcp.json), NINE_ROUTER_URL, or
  management API integration from agents.
---

# 9Router (gateway + MCP)

## MCP server (FastMCP)

- **Code:** `mcp/nine_router_mcp/` — entrypoint `mcp/nine_router_mcp/server.py`.
- **Install (editable):** from repo root, `cd mcp && pip install -e .`
- **Run locally:** `cd mcp && fastmcp run nine_router_mcp/server.py` (or use the absolute-path form below for Cursor).
- **Env:** `NINE_ROUTER_URL` — base URL of a running 9Router instance (default in docs: `http://localhost:20128`). Management tools assume `requireLogin` is off for local use.

## Cursor `mcp.json` (required shape)

Cursor reads **`~/.cursor/mcp.json`** (global) and **`.cursor/mcp.json`** in the project (merged). Prefer the **project** file so the team shares one config.

**Do not rely on `cwd` alone** for the script path. Some Cursor builds start user-scoped MCP with an effective cwd of `$HOME`, so `nine_router_mcp/server.py` resolves to **`$HOME/nine_router_mcp/server.py`** and fails.

Use:

1. **`args`:** `fastmcp run <absolute-path-to-server.py>` with Cursor interpolation, e.g. `${workspaceFolder}/mcp/nine_router_mcp/server.py`.
2. **`PYTHONPATH`:** set to the **`mcp/`** directory (same interpolation), so `from nine_router_mcp.tools import …` resolves even if `cwd` is wrong.
3. **`cwd`:** still set to `${workspaceFolder}/mcp` when supported (harmless if ignored).

### Project `.cursor/mcp.json` (this repo)

```json
{
  "mcpServers": {
    "9router": {
      "command": "fastmcp",
      "args": ["run", "${workspaceFolder}/mcp/nine_router_mcp/server.py"],
      "cwd": "${workspaceFolder}/mcp",
      "env": {
        "NINE_ROUTER_URL": "http://localhost:20128",
        "PYTHONPATH": "${workspaceFolder}/mcp"
      }
    }
  }
}
```

### User `~/.cursor/mcp.json` (optional)

If you duplicate the `9router` server globally, use **`${userHome}`** (or an absolute path) instead of `${workspaceFolder}`. Avoid defining **two** conflicting `9router` entries unless you understand merge behavior.

## Troubleshooting

| Symptom | Likely cause | Fix |
|--------|----------------|-----|
| `File not found: .../Users/<you>/nine_router_mcp/server.py` | Relative script path + wrong cwd | Use absolute `args` path + `PYTHONPATH` as above |
| Tools return connection errors | 9Router not running | Start app; check `NINE_ROUTER_URL` |
| 401 from management APIs | Dashboard login required | Disable or account for `requireLogin` in settings |

## References

- Repo: `mcp/README.md` — setup, env table, generic `mcp.json` example.
- Agent context: root `CLAUDE.md` — dev URLs and architecture.
