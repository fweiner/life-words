"""Fire-and-forget error logger.

Logs errors to the error_logs table with full context. Design principles:
- Never raises exceptions (triple try/except safety)
- Non-blocking (asyncio.create_task for DB writes)
- Auto-sanitizes sensitive fields from request bodies
- Auto-truncates long strings
"""
import asyncio
import logging
import re
import traceback
from typing import Any, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

SENSITIVE_KEYS = re.compile(
    r"(password|secret|token|api_key|access_token|refresh_token"
    r"|authorization|credit_card|ssn|cvv)",
    re.IGNORECASE,
)


def _sanitize(obj: Any) -> Any:
    """Recursively redact sensitive fields from dicts/lists."""
    if isinstance(obj, dict):
        return {
            k: "***REDACTED***" if SENSITIVE_KEYS.search(k) else _sanitize(v)
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [_sanitize(item) for item in obj]
    return obj


def _truncate(value: Optional[str], limit: int) -> Optional[str]:
    """Truncate a string, appending a note if it was cut."""
    if value is None or len(value) <= limit:
        return value
    return value[:limit] + f"... [truncated, {len(value)} chars total]"


async def _insert_error_log(data: dict) -> None:
    """POST the error log row to Supabase REST API."""
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{settings.supabase_url}/rest/v1/error_logs",
                headers={
                    "apikey": settings.supabase_secret_key,
                    "Authorization": f"Bearer {settings.supabase_secret_key}",
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal",
                },
                json=data,
                timeout=5.0,
            )
    except Exception:
        logger.error("Failed to insert error log", exc_info=True)


def log_error(
    *,
    error: Exception | str,
    source: str = "manual",
    service_name: Optional[str] = None,
    function_name: Optional[str] = None,
    endpoint: Optional[str] = None,
    http_method: Optional[str] = None,
    request_body: Any = None,
    query_params: Optional[dict] = None,
    status_code: Optional[int] = None,
    user_id: Optional[str] = None,
    user_email: Optional[str] = None,
) -> None:
    """Log an error to the database. Fire-and-forget — never raises."""
    try:
        if isinstance(error, Exception):
            error_message = str(error)
            error_type = type(error).__name__
            stack = traceback.format_exception(
                type(error), error, error.__traceback__
            )
            stacktrace = "".join(stack)
        else:
            error_message = error
            error_type = None
            stacktrace = None

        data = {
            "error_message": _truncate(error_message, 2000),
            "error_type": error_type,
            "stacktrace": _truncate(stacktrace, 10000),
            "endpoint": endpoint,
            "http_method": http_method,
            "request_body": _sanitize(request_body) if request_body else None,
            "query_params": query_params,
            "status_code": status_code,
            "user_id": user_id,
            "user_email": user_email,
            "source": source,
            "service_name": service_name,
            "function_name": function_name,
            "environment": settings.environment,
        }

        try:
            loop = asyncio.get_running_loop()
            loop.create_task(_insert_error_log(data))
        except RuntimeError:
            # No event loop — fall back to standard logging
            logger.error(
                "Error log (no loop): %s — %s", error_type, error_message
            )
    except Exception:
        # Outermost safety net — logging must never crash the app
        try:
            logger.error("log_error itself failed", exc_info=True)
        except Exception:
            pass
