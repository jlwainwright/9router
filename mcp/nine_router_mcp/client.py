"""Shared httpx client for 9Router API calls."""
import os
import httpx

NINE_ROUTER_URL = os.environ.get("NINE_ROUTER_URL", "http://localhost:20128").rstrip("/")

_client: httpx.AsyncClient | None = None


def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(base_url=NINE_ROUTER_URL, timeout=30.0)
    return _client


def fmt_error(status: int, body: dict, resource: str = "", resource_id: str = "") -> str:
    """Return a consistent, actionable error string."""
    if status == 0:
        return body.get("error", f"Cannot reach 9Router at {NINE_ROUTER_URL}. Is it running?")
    if status == 400:
        return body.get("error", "Bad request — check your parameters.")
    if status == 401:
        return "9Router returned 401. Login may be required — check requireLogin in settings or disable it."
    if status == 404:
        resource_label = resource.replace("_", " ").title() if resource else "Resource"
        hint = f" Use list_{resource}s to see valid IDs." if resource else ""
        label = f" '{resource_id}'" if resource_id else ""
        return f"{resource_label}{label} not found.{hint}"
    if status == 409:
        return "Cannot delete — resource is still in use. Remove it from bound providers first."
    if status == 500:
        return "9Router returned an internal error. Check server logs."
    return body.get("error", f"Unexpected error (HTTP {status}).")


async def api_get(path: str, params: dict | None = None) -> tuple[int, dict]:
    client = get_client()
    try:
        r = await client.get(path, params=params)
        try:
            body = r.json()
        except Exception:
            body = {"error": r.text or f"Non-JSON response (HTTP {r.status_code})"}
        return r.status_code, body
    except httpx.HTTPError:
        return 0, {"error": f"Cannot reach 9Router at {NINE_ROUTER_URL}. Is it running?"}


async def api_post(path: str, json: dict | None = None) -> tuple[int, dict]:
    client = get_client()
    try:
        r = await client.post(path, json=json or {})
        try:
            body = r.json()
        except Exception:
            body = {"error": r.text or f"Non-JSON response (HTTP {r.status_code})"}
        return r.status_code, body
    except httpx.HTTPError:
        return 0, {"error": f"Cannot reach 9Router at {NINE_ROUTER_URL}. Is it running?"}


async def api_put(path: str, json: dict | None = None) -> tuple[int, dict]:
    client = get_client()
    try:
        r = await client.put(path, json=json or {})
        try:
            body = r.json()
        except Exception:
            body = {"error": r.text or f"Non-JSON response (HTTP {r.status_code})"}
        return r.status_code, body
    except httpx.HTTPError:
        return 0, {"error": f"Cannot reach 9Router at {NINE_ROUTER_URL}. Is it running?"}


async def api_patch(path: str, json: dict | None = None) -> tuple[int, dict]:
    client = get_client()
    try:
        r = await client.patch(path, json=json or {})
        try:
            body = r.json()
        except Exception:
            body = {"error": r.text or f"Non-JSON response (HTTP {r.status_code})"}
        return r.status_code, body
    except httpx.HTTPError:
        return 0, {"error": f"Cannot reach 9Router at {NINE_ROUTER_URL}. Is it running?"}


async def api_delete(path: str, params: dict | None = None) -> tuple[int, dict]:
    client = get_client()
    try:
        r = await client.delete(path, params=params)
        try:
            body = r.json() if r.content else {}
        except Exception:
            body = {"error": r.text or f"Non-JSON response (HTTP {r.status_code})"}
        return r.status_code, body
    except httpx.HTTPError:
        return 0, {"error": f"Cannot reach 9Router at {NINE_ROUTER_URL}. Is it running?"}
