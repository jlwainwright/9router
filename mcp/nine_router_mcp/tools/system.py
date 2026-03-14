"""System tools: version, proxy pools, tunnel."""
from fastmcp import FastMCP
from nine_router_mcp.client import api_get, api_post, api_put, api_delete, fmt_error

mcp = FastMCP("system")


@mcp.tool(description="Get current and latest 9Router version. Indicates if an update is available.")
async def get_version() -> str:
    status, body = await api_get("/api/version")
    if status != 200:
        return fmt_error(status, body)
    current = body.get("currentVersion", "unknown")
    latest = body.get("latestVersion", "unknown")
    has_update = body.get("hasUpdate", False)
    update_note = f"\n⚠️ Update available: {latest}" if has_update else "\n✓ Up to date."
    return f"**Current version:** {current}\n**Latest version:** {latest}{update_note}"


@mcp.tool(description="List all proxy pools with id, name, proxy URL, isActive, and bound connection count.")
async def list_proxy_pools() -> str:
    status, body = await api_get("/api/proxy-pools", params={"includeUsage": "true"})
    if status != 200:
        return fmt_error(status, body, "proxy_pool")
    pools = body.get("proxyPools", [])
    if not pools:
        return "No proxy pools configured."
    lines = ["| ID | Name | Proxy URL | Active | Connections |", "|---|---|---|---|---|"]
    for p in pools:
        lines.append(f"| {p.get('id','')} | {p.get('name','')} | {p.get('proxyUrl','')} | {p.get('isActive','')} | {p.get('boundConnectionCount',0)} |")
    return "\n".join(lines)


@mcp.tool(description="Get a single proxy pool by ID.")
async def get_proxy_pool(id: str) -> str:
    status, body = await api_get(f"/api/proxy-pools/{id}")
    if status != 200:
        return fmt_error(status, body, "proxy_pool", resource_id=id)
    pool = body.get("proxyPool", body)
    return "\n".join(f"**{k}:** {v}" for k, v in pool.items())


@mcp.tool(description=(
    "Create a new proxy pool. "
    "name: display name. proxy_url: HTTP/HTTPS proxy URL. "
    "no_proxy: comma-separated hosts to bypass (optional). "
    "strict_proxy: fail requests that bypass the proxy (default False)."
))
async def create_proxy_pool(name: str, proxy_url: str, no_proxy: str = "", strict_proxy: bool = False) -> str:
    payload = {"name": name, "proxyUrl": proxy_url, "noProxy": no_proxy, "strictProxy": strict_proxy}
    status, body = await api_post("/api/proxy-pools", json=payload)
    if status not in (200, 201):
        return fmt_error(status, body, "proxy_pool")
    pool = body.get("proxyPool", body)
    return f"✓ Proxy pool created: {pool.get('name')} (id={pool.get('id')})"


@mcp.tool(description="Update a proxy pool by ID. Supply only fields to change: name, proxy_url, no_proxy, is_active.")
async def update_proxy_pool(
    id: str,
    name: str = "",
    proxy_url: str = "",
    no_proxy: str = "",
    is_active: bool | None = None,
) -> str:
    payload: dict = {}
    if name:
        payload["name"] = name
    if proxy_url:
        payload["proxyUrl"] = proxy_url
    if no_proxy:
        payload["noProxy"] = no_proxy
    if is_active is not None:
        payload["isActive"] = is_active
    if not payload:
        return "No fields to update — provide at least one of: name, proxy_url, no_proxy, is_active."
    status, body = await api_put(f"/api/proxy-pools/{id}", json=payload)
    if status != 200:
        return fmt_error(status, body, "proxy_pool", resource_id=id)
    return f"✓ Proxy pool {id} updated."


@mcp.tool(description=(
    "Delete a proxy pool by ID. "
    "Returns error if pool is still assigned to provider connections (409). "
    "Use list_providers to find and unassign affected connections first."
))
async def delete_proxy_pool(id: str) -> str:
    status, body = await api_delete(f"/api/proxy-pools/{id}")
    if status not in (200, 204):
        return fmt_error(status, body, "proxy_pool", resource_id=id)
    return f"✓ Proxy pool {id} deleted."


@mcp.tool(description="Get current tunnel status (enabled/disabled).")
async def get_tunnel_status() -> str:
    status, body = await api_get("/api/tunnel/status")
    if status != 200:
        return fmt_error(status, body)
    enabled = body.get("enabled", body.get("active", body.get("status") == "active"))
    return f"Tunnel is currently **{'enabled' if enabled else 'disabled'}**."


@mcp.tool(description="Enable or disable the 9Router tunnel. enabled=True to turn on, enabled=False to turn off.")
async def set_tunnel(enabled: bool) -> str:
    path = "/api/tunnel/enable" if enabled else "/api/tunnel/disable"
    status, body = await api_post(path)
    if status not in (200, 201):
        return fmt_error(status, body)
    return f"✓ Tunnel {'enabled' if enabled else 'disabled'}."
