"""9Router MCP Server entry point."""
from fastmcp import FastMCP
from nine_router_mcp.tools import providers, combos, keys, models, usage, settings, system

mcp = FastMCP(
    "9router",
    instructions=(
        "This server manages a running 9Router AI gateway. "
        "Use list_* tools first to discover IDs before calling get/update/delete. "
        "9Router must be running at NINE_ROUTER_URL (default http://localhost:20128) "
        "with requireLogin disabled."
    ),
)

mcp.mount(providers.mcp, namespace="providers")
mcp.mount(combos.mcp, namespace="combos")
mcp.mount(keys.mcp, namespace="keys")
mcp.mount(models.mcp, namespace="models")
mcp.mount(usage.mcp, namespace="usage")
mcp.mount(settings.mcp, namespace="settings")
mcp.mount(system.mcp, namespace="system")


def main():
    mcp.run()


if __name__ == "__main__":
    main()
