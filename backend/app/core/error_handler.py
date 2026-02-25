"""Error logging middleware that captures unhandled exceptions to the database."""
import traceback

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.database import db


class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs unhandled exceptions to the error_logs table."""

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            error_message = str(exc)[:2000]
            tb = traceback.format_exc()[:10000]

            # Extract user_id from auth header if possible
            user_id = None
            if hasattr(request.state, "user_id"):
                user_id = request.state.user_id

            # Best-effort insert — don't mask the original error
            try:
                await db.insert("error_logs", {
                    "endpoint": str(request.url.path),
                    "method": request.method,
                    "status_code": 500,
                    "error_message": error_message,
                    "traceback": tb,
                    "user_id": user_id,
                })
            except Exception:
                pass

            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"},
            )
