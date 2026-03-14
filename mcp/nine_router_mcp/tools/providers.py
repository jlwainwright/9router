"""Provider connection and node management tools."""
from fastmcp import FastMCP
from nine_router_mcp.client import api_get, api_post, api_put, api_delete, fmt_error

mcp = FastMCP("providers")


def _safe_connection(c: dict) -> dict:
    """Strip sensitive fields from a provider connection."""
    return {k: v for k, v in c.items() if k not in ("apiKey", "accessToken", "refreshToken", "idToken")}


@mcp.tool(description="List all provider connections. Returns name, provider type, isActive, and priority for each.")
async def list_providers() -> str:
    status, body = await api_get("/api/providers")
    if status != 200:
        return fmt_error(status, body, "provider")
    conns = body.get("connections", [])
    if not conns:
        return "No provider connections configured."
    lines = ["| ID | Name | Provider | Active | Priority |", "|---|---|---|---|---|"]
    for c in conns:
        lines.append(f"| {c.get('id','')} | {c.get('name','')} | {c.get('provider','')} | {c.get('isActive','')} | {c.get('priority','')} |")
    return "\n".join(lines)


@mcp.tool(description="Get a single provider connection by ID. Returns full details excluding secrets.")
async def get_provider(id: str) -> str:
    status, body = await api_get(f"/api/providers/{id}")
    if status != 200:
        return fmt_error(status, body, "provider", resource_id=id)
    c = _safe_connection(body.get("connection", body))
    return "\n".join(f"**{k}:** {v}" for k, v in c.items())


@mcp.tool(description=(
    "Create a new API key provider connection. "
    "provider: provider type (e.g. 'openai', 'anthropic', 'glm'). "
    "name: display name. api_key: the provider API key. "
    "priority: 1=highest (default 1). "
    "default_model: optional default model string."
))
async def create_provider(provider: str, name: str, api_key: str, priority: int = 1, default_model: str = "") -> str:
    payload: dict = {"provider": provider, "name": name, "apiKey": api_key, "priority": priority}
    if default_model:
        payload["defaultModel"] = default_model
    status, body = await api_post("/api/providers", json=payload)
    if status not in (200, 201):
        return fmt_error(status, body, "provider")
    c = _safe_connection(body.get("connection", body))
    return f"✓ Provider created: {c.get('name')} (id={c.get('id')})"


@mcp.tool(description=(
    "Update an existing provider connection. "
    "Only supply fields you want to change. "
    "Updatable: name, priority, is_active, api_key, default_model."
))
async def update_provider(
    id: str,
    name: str = "",
    priority: int = 0,
    is_active: bool | None = None,
    api_key: str = "",
    default_model: str = "",
) -> str:
    payload: dict = {}
    if name:
        payload["name"] = name
    if priority:
        payload["priority"] = priority
    if is_active is not None:
        payload["isActive"] = is_active
    if api_key:
        payload["apiKey"] = api_key
    if default_model:
        payload["defaultModel"] = default_model
    if not payload:
        return "No fields to update — provide at least one of: name, priority, is_active, api_key, default_model."
    status, body = await api_put(f"/api/providers/{id}", json=payload)
    if status != 200:
        return fmt_error(status, body, "provider", resource_id=id)
    return f"✓ Provider {id} updated."


@mcp.tool(description="Delete a provider connection by ID. This is irreversible.")
async def delete_provider(id: str) -> str:
    status, body = await api_delete(f"/api/providers/{id}")
    if status not in (200, 204):
        return fmt_error(status, body, "provider", resource_id=id)
    return f"✓ Provider {id} deleted."


@mcp.tool(description="Run a connectivity test on a provider connection. Returns test result and any error message.")
async def test_provider(id: str) -> str:
    status, body = await api_post(f"/api/providers/{id}/test")
    if status not in (200, 201):
        return fmt_error(status, body, "provider", resource_id=id)
    success = body.get("success", body.get("status") == "ok")
    error = body.get("error", "")
    if success:
        return f"✓ Provider {id} test passed."
    return f"✗ Provider {id} test failed: {error}"


@mcp.tool(description="List all custom provider nodes (OpenAI-compatible and Anthropic-compatible endpoints).")
async def list_provider_nodes() -> str:
    status, body = await api_get("/api/provider-nodes")
    if status != 200:
        return fmt_error(status, body, "provider_node")
    nodes = body.get("nodes", [])
    if not nodes:
        return "No provider nodes configured."
    lines = ["| ID | Name | Type | Prefix | Base URL |", "|---|---|---|---|---|"]
    for n in nodes:
        lines.append(f"| {n.get('id','')} | {n.get('name','')} | {n.get('type','')} | {n.get('prefix','')} | {n.get('baseUrl','')} |")
    return "\n".join(lines)


@mcp.tool(description=(
    "Create a new custom provider node. "
    "name: display name. prefix: model prefix (e.g. 'myapi'). "
    "node_type: 'openai-compatible' or 'anthropic-compatible'. "
    "base_url: API base URL. "
    "api_type: 'chat' or 'responses' (openai-compatible only)."
))
async def create_provider_node(name: str, prefix: str, node_type: str, base_url: str, api_type: str = "chat") -> str:
    payload: dict = {"name": name, "prefix": prefix, "type": node_type, "baseUrl": base_url}
    if node_type == "openai-compatible":
        payload["apiType"] = api_type
    status, body = await api_post("/api/provider-nodes", json=payload)
    if status not in (200, 201):
        return fmt_error(status, body, "provider_node")
    node = body.get("node", body)
    return f"✓ Provider node created: {node.get('name')} (id={node.get('id')})"


@mcp.tool(description="Update a custom provider node by ID. Supply only fields to change: name, base_url.")
async def update_provider_node(id: str, name: str = "", base_url: str = "") -> str:
    payload: dict = {}
    if name:
        payload["name"] = name
    if base_url:
        payload["baseUrl"] = base_url
    if not payload:
        return "No fields to update — provide name or base_url."
    status, body = await api_put(f"/api/provider-nodes/{id}", json=payload)
    if status != 200:
        return fmt_error(status, body, "provider_node", resource_id=id)
    return f"✓ Provider node {id} updated."


@mcp.tool(description="Delete a custom provider node by ID.")
async def delete_provider_node(id: str) -> str:
    status, body = await api_delete(f"/api/provider-nodes/{id}")
    if status not in (200, 204):
        return fmt_error(status, body, "provider_node", resource_id=id)
    return f"✓ Provider node {id} deleted."
