"""API key management tools."""
from fastmcp import FastMCP
from nine_router_mcp.client import api_get, api_post, api_delete, fmt_error

mcp = FastMCP("keys")


@mcp.tool(description="List all 9Router API keys. Returns id, name, and creation info (not the key value itself).")
async def list_api_keys() -> str:
    status, body = await api_get("/api/keys")
    if status != 200:
        return fmt_error(status, body, "key")
    keys = body.get("keys", [])
    if not keys:
        return "No API keys configured."
    lines = ["| ID | Name | Created |", "|---|---|---|"]
    for k in keys:
        lines.append(f"| {k.get('id','')} | {k.get('name','')} | {k.get('createdAt','')} |")
    return "\n".join(lines)


@mcp.tool(description=(
    "Create a new 9Router API key. "
    "name: descriptive label for this key. "
    "Returns the key value — save it immediately, it won't be shown again."
))
async def create_api_key(name: str) -> str:
    status, body = await api_post("/api/keys", json={"name": name})
    if status not in (200, 201):
        return fmt_error(status, body, "key")
    return (
        f"✓ API key created:\n"
        f"Name: {body.get('name')}\n"
        f"Key: {body.get('key')}\n"
        f"ID: {body.get('id')}\n\n"
        f"⚠️ Save this key — it will not be shown again."
    )


@mcp.tool(description="Delete (revoke) an API key by ID. This is irreversible.")
async def delete_api_key(id: str) -> str:
    status, body = await api_delete(f"/api/keys/{id}")
    if status not in (200, 204):
        return fmt_error(status, body, "key", resource_id=id)
    return f"✓ API key {id} deleted."
