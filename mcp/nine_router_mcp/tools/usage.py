"""Usage stats, logs, and history tools."""
from fastmcp import FastMCP
from nine_router_mcp.client import api_get, fmt_error

mcp = FastMCP("usage")

VALID_PERIODS = ("24h", "7d", "30d", "60d", "all")


@mcp.tool(description=(
    "Get token usage statistics for a time period. "
    "period: one of '24h', '7d', '30d', '60d', 'all' (default '7d'). "
    "Returns total requests, input/output tokens, and per-provider breakdown."
))
async def get_usage_stats(period: str = "7d") -> str:
    if period not in VALID_PERIODS:
        return f"Invalid period '{period}'. Must be one of: {', '.join(VALID_PERIODS)}."
    status, body = await api_get("/api/usage/stats", params={"period": period})
    if status != 200:
        return fmt_error(status, body)
    lines = [f"## Usage Stats ({period})"]
    for k, v in body.items():
        if not isinstance(v, (dict, list)):
            lines.append(f"**{k}:** {v}")
    providers = body.get("byProvider") or body.get("providers") or {}
    if providers:
        lines.append("\n### By Provider")
        lines.append("| Provider | Requests | Tokens In | Tokens Out |")
        lines.append("|---|---|---|---|")
        for p, stats in providers.items():
            if isinstance(stats, dict):
                lines.append(f"| {p} | {stats.get('requests','')} | {stats.get('tokensIn','')} | {stats.get('tokensOut','')} |")
    return "\n".join(lines)


@mcp.tool(description=(
    "Get the most recent request log entries (last 200). "
    "Shows timestamp, model, provider, token counts, and status for each request."
))
async def get_usage_logs() -> str:
    status, body = await api_get("/api/usage/logs")
    if status != 200:
        return fmt_error(status, body)
    logs = body if isinstance(body, list) else body.get("logs", [])
    if not logs:
        return "No log entries found."
    lines = ["| Time | Model | Provider | Status | In | Out |", "|---|---|---|---|---|---|"]
    for entry in logs:
        lines.append(
            f"| {entry.get('timestamp','') or entry.get('time','')} "
            f"| {entry.get('model','')} "
            f"| {entry.get('provider','')} "
            f"| {entry.get('status','')} "
            f"| {entry.get('tokensIn', entry.get('in',''))} "
            f"| {entry.get('tokensOut', entry.get('out',''))} |"
        )
    return "\n".join(lines)


@mcp.tool(description="Get usage history chart data. Returns time-series token usage data.")
async def get_usage_history() -> str:
    status, body = await api_get("/api/usage/history")
    if status != 200:
        return fmt_error(status, body)
    data = body if isinstance(body, list) else body.get("history", body.get("data", []))
    if not data:
        return "No usage history available."
    lines = ["## Usage History", "| Date | Requests | Tokens In | Tokens Out |", "|---|---|---|---|"]
    for entry in (data if isinstance(data, list) else []):
        if isinstance(entry, dict):
            lines.append(f"| {entry.get('date',entry.get('time',''))} | {entry.get('requests','')} | {entry.get('tokensIn','')} | {entry.get('tokensOut','')} |")
    return "\n".join(lines)


@mcp.tool(description=(
    "Get full details for a specific request by its log ID. "
    "request_id: the log entry ID from get_usage_logs. "
    "Returns full request/response details including messages, tools used, and timing."
))
async def get_request_details(request_id: str) -> str:
    status, body = await api_get("/api/usage/request-details", params={"id": request_id})
    if status != 200:
        return fmt_error(status, body, "request", resource_id=request_id)
    lines = [f"## Request {request_id}"]
    for k, v in body.items():
        if isinstance(v, (str, int, float, bool)):
            lines.append(f"**{k}:** {v}")
        elif isinstance(v, list) and len(v) < 5:
            lines.append(f"**{k}:** {v}")
    return "\n".join(lines)
