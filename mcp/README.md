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

Add to your `.mcp.json`:

```json
{
  "mcpServers": {
    "9router": {
      "command": "fastmcp",
      "args": ["run", "nine_router_mcp/server.py"],
      "cwd": "/path/to/9router-fork/mcp",
      "env": {
        "NINE_ROUTER_URL": "http://localhost:20128"
      }
    }
  }
}
```
