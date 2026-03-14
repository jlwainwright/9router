"""Global settings management tools. Password fields are explicitly excluded."""
from fastmcp import FastMCP
from nine_router_mcp.client import api_get, api_patch, fmt_error

mcp = FastMCP("settings")

_FORBIDDEN_KEYS = {"newPassword", "currentPassword", "password"}


@mcp.tool(description=(
    "Get current 9Router global settings. "
    "Returns proxy config, locale, requireLogin, and other runtime settings. "
    "Password hash is never returned."
))
async def get_settings() -> str:
    status, body = await api_get("/api/settings")
    if status != 200:
        return fmt_error(status, body)
    lines = ["## 9Router Settings"]
    for k, v in body.items():
        if k not in _FORBIDDEN_KEYS:
            lines.append(f"**{k}:** {v}")
    return "\n".join(lines)


@mcp.tool(description=(
    "Update 9Router global settings. Supply only the fields you want to change. "
    "Common fields: outbound_proxy_enabled (bool), outbound_proxy_url (str), "
    "outbound_no_proxy (str), require_login (bool), locale (str). "
    "Password changes are not supported through this tool."
))
async def update_settings(
    outbound_proxy_enabled: bool | None = None,
    outbound_proxy_url: str = "",
    outbound_no_proxy: str = "",
    require_login: bool | None = None,
    locale: str = "",
) -> str:
    payload: dict = {}
    if outbound_proxy_enabled is not None:
        payload["outboundProxyEnabled"] = outbound_proxy_enabled
    if outbound_proxy_url:
        payload["outboundProxyUrl"] = outbound_proxy_url
    if outbound_no_proxy:
        payload["outboundNoProxy"] = outbound_no_proxy
    if require_login is not None:
        payload["requireLogin"] = require_login
    if locale:
        payload["locale"] = locale
    if not payload:
        return "No settings to update — provide at least one field."
    status, body = await api_patch("/api/settings", json=payload)
    if status != 200:
        return fmt_error(status, body)
    return "✓ Settings updated: " + ", ".join(payload.keys())
