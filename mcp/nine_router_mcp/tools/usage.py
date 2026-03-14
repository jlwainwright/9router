"""Usage stats, logs, and history tools."""
from fastmcp import FastMCP
from nine_router_mcp.client import api_get, fmt_error

mcp = FastMCP("usage")

VALID_PERIODS = ("24h", "7d", "30d", "60d", "all")


@mcp.tool(description=(
    "Get token usage statistics for a time period. "
    "period: one of '24h', '7d', '30d', '60d', 'all' (default '7d'). "
    "Returns total requests, prompt tokens, completion tokens, and per-provider breakdown."
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
    providers = body.get("byProvider") or {}
    if providers:
        lines.append("\n### By Provider")
        lines.append("| Provider | Requests | Prompt Tokens | Completion Tokens |")
        lines.append("|---|---|---|---|")
        for p, stats in providers.items():
            if isinstance(stats, dict):
                lines.append(
                    f"| {p} "
                    f"| {stats.get('requests','')} "
                    f"| {stats.get('promptTokens','')} "
                    f"| {stats.get('completionTokens','')} |"
                )
    return "\n".join(lines)


@mcp.tool(description=(
    "Get the most recent request log entries (last 200). "
    "Each entry shows: datetime, model, provider, account, tokens sent, tokens received, status. "
    "Log format: 'datetime | model | PROVIDER | account | sent | received | status'."
))
async def get_usage_logs() -> str:
    status, body = await api_get("/api/usage/logs")
    if status != 200:
        return fmt_error(status, body)
    logs = body if isinstance(body, list) else body.get("logs", [])
    if not logs:
        return "No log entries found."
    lines = ["| Time | Model | Provider | Account | Sent | Received | Status |",
             "|---|---|---|---|---|---|---|"]
    for entry in logs:
        if not isinstance(entry, str):
            continue
        parts = [p.strip() for p in entry.split("|")]
        if len(parts) >= 7:
            lines.append(
                f"| {parts[0]} | {parts[1]} | {parts[2]} "
                f"| {parts[3]} | {parts[4]} | {parts[5]} | {parts[6]} |"
            )
        else:
            lines.append(f"| {entry} | | | | | | |")
    return "\n".join(lines)


@mcp.tool(description=(
    "Get all-time usage statistics (same as get_usage_stats with period='all', no period parameter). "
    "Returns total requests, prompt tokens, completion tokens across all time."
))
async def get_usage_history() -> str:
    status, body = await api_get("/api/usage/history")
    if status != 200:
        return fmt_error(status, body)
    lines = ["## All-Time Usage Stats"]
    for k, v in body.items():
        if not isinstance(v, (dict, list)):
            lines.append(f"**{k}:** {v}")
    return "\n".join(lines)


@mcp.tool(description=(
    "List request details with optional filters. "
    "Returns paginated list of detailed request records from the SQLite usage database. "
    "Filters: provider (string), model (string), connection_id (string), "
    "status (string, e.g. 'success' or 'error'), "
    "start_date (ISO date string), end_date (ISO date string). "
    "page: page number (default 1). page_size: results per page, 1-100 (default 20)."
))
async def list_request_details(
    page: int = 1,
    page_size: int = 20,
    provider: str = "",
    model: str = "",
    connection_id: str = "",
    status_filter: str = "",
    start_date: str = "",
    end_date: str = "",
) -> str:
    params: dict = {"page": page, "pageSize": page_size}
    if provider:
        params["provider"] = provider
    if model:
        params["model"] = model
    if connection_id:
        params["connectionId"] = connection_id
    if status_filter:
        params["status"] = status_filter
    if start_date:
        params["startDate"] = start_date
    if end_date:
        params["endDate"] = end_date
    status, body = await api_get("/api/usage/request-details", params=params)
    if status != 200:
        return fmt_error(status, body)
    records = body.get("details", [])
    total = body.get("pagination", {}).get("totalItems", len(records))
    if not records:
        return "No request records found."
    lines = [
        f"## Request Details (page {page}, {len(records)} of {total} total)",
        "| Time | Model | Provider | Status | Prompt | Completion |",
        "|---|---|---|---|---|---|",
    ]
    for r in records:
        if isinstance(r, dict):
            tokens = r.get('tokens') or {}
            prompt = tokens.get('prompt_tokens', tokens.get('input_tokens', ''))
            completion = tokens.get('completion_tokens', tokens.get('output_tokens', ''))
            lines.append(
                f"| {r.get('timestamp', r.get('createdAt', ''))} "
                f"| {r.get('model', '')} "
                f"| {r.get('provider', '')} "
                f"| {r.get('status', '')} "
                f"| {prompt} "
                f"| {completion} |"
            )
    return "\n".join(lines)
