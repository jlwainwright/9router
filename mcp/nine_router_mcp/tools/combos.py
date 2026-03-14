"""Combo (model fallback chain) management tools."""
from fastmcp import FastMCP
from nine_router_mcp.client import api_get, api_post, api_put, api_delete, fmt_error

mcp = FastMCP("combos")


@mcp.tool(description="List all combos. Each combo is a named fallback chain of models.")
async def list_combos() -> str:
    status, body = await api_get("/api/combos")
    if status != 200:
        return fmt_error(status, body, "combo")
    combos = body.get("combos", [])
    if not combos:
        return "No combos configured."
    lines = ["| ID | Name | Models |", "|---|---|---|"]
    for c in combos:
        models = ", ".join(c.get("models", []))
        lines.append(f"| {c.get('id','')} | {c.get('name','')} | {models} |")
    return "\n".join(lines)


@mcp.tool(description="Get a single combo by ID including its full model list.")
async def get_combo(id: str) -> str:
    status, body = await api_get(f"/api/combos/{id}")
    if status != 200:
        return fmt_error(status, body, "combo", resource_id=id)
    c = body.get("combo", body)
    models = "\n".join(f"  {i+1}. {m}" for i, m in enumerate(c.get("models", [])))
    return f"**{c.get('name')}** (id={c.get('id')})\nModels:\n{models}"


@mcp.tool(description=(
    "Create a new combo. "
    "name: unique name (letters, numbers, - and _ only). "
    "models: ordered list of model strings e.g. ['cc/claude-sonnet-4-6', 'glm/glm-4.7']. "
    "First model is tried first; subsequent models are fallbacks."
))
async def create_combo(name: str, models: list[str]) -> str:
    status, body = await api_post("/api/combos", json={"name": name, "models": models})
    if status not in (200, 201):
        return fmt_error(status, body, "combo")
    combo = body.get("combo", body)
    return f"✓ Combo '{name}' created (id={combo.get('id')}) with {len(models)} model(s)."


@mcp.tool(description=(
    "Update an existing combo. Supply only fields to change. "
    "name: new unique name. models: new ordered model list (replaces existing)."
))
async def update_combo(id: str, name: str = "", models: list[str] | None = None) -> str:
    payload: dict = {}
    if name:
        payload["name"] = name
    if models is not None:
        payload["models"] = models
    if not payload:
        return "No fields to update — provide name or models."
    status, body = await api_put(f"/api/combos/{id}", json=payload)
    if status != 200:
        return fmt_error(status, body, "combo", resource_id=id)
    return f"✓ Combo {id} updated."


@mcp.tool(description="Delete a combo by ID.")
async def delete_combo(id: str) -> str:
    status, body = await api_delete(f"/api/combos/{id}")
    if status not in (200, 204):
        return fmt_error(status, body, "combo", resource_id=id)
    return f"✓ Combo {id} deleted."
