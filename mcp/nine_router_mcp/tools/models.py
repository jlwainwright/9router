"""Model listing and alias management tools."""
from fastmcp import FastMCP
from nine_router_mcp.client import api_get, api_put, api_delete, fmt_error

mcp = FastMCP("models")


@mcp.tool(description=(
    "List all available models with their current aliases. "
    "Models are in provider/model-id format (e.g. cc/claude-sonnet-4-6). "
    "Alias is the name clients can use instead of the full model string."
))
async def list_models() -> str:
    status, body = await api_get("/api/models")
    if status != 200:
        return fmt_error(status, body, "model")
    models = body.get("models", [])
    if not models:
        return "No models available."
    lines = ["| Full Model | Provider | Alias |", "|---|---|---|"]
    for m in models:
        lines.append(f"| {m.get('fullModel','')} | {m.get('provider','')} | {m.get('alias','')} |")
    return "\n".join(lines)


@mcp.tool(description=(
    "Set an alias for a model. "
    "model: full model string e.g. 'cc/claude-sonnet-4-6'. "
    "alias: the new alias name clients can use to reference this model. "
    "Alias must be unique across all models."
))
async def set_model_alias(model: str, alias: str) -> str:
    status, body = await api_put("/api/models/alias", json={"model": model, "alias": alias})
    if status != 200:
        return fmt_error(status, body, "model", resource_id=model)
    return f"✓ Alias '{alias}' set for model '{model}'."


@mcp.tool(description=(
    "Delete a model alias by its alias name. "
    "alias: the alias string to remove (not the model ID). "
    "After deletion, the model reverts to its full model string."
))
async def delete_model_alias(alias: str) -> str:
    status, body = await api_delete("/api/models/alias", params={"alias": alias})
    if status not in (200, 204):
        return fmt_error(status, body, "model", resource_id=alias)
    return f"✓ Alias '{alias}' deleted."
