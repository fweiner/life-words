"""Authentication utilities for JWT verification."""
import jwt
import httpx
from typing import Optional, Dict, Any
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings


security = HTTPBearer()


async def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify Supabase JWT token.

    With new Supabase API keys (sb_secret_*), we verify tokens by calling
    the Supabase Auth API directly as recommended in the documentation.
    """
    try:
        # Verify token with Supabase Auth API
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.supabase_url}/auth/v1/user",
                headers={
                    "apikey": settings.supabase_secret_key,
                    "Authorization": f"Bearer {token}"
                }
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=401,
                    detail=f"Token verification failed: {response.text}"
                )

            user_data = response.json()

            # Return payload in expected format
            return {
                "sub": user_data.get("id"),
                "email": user_data.get("email"),
                "role": user_data.get("role", "authenticated"),
                "aud": "authenticated"
            }

    except httpx.HTTPError as e:
        raise HTTPException(status_code=401, detail=f"Token verification error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> Dict[str, Any]:
    """Get current user from JWT token."""
    token = credentials.credentials
    payload = await verify_token(token)

    # Extract user info from JWT payload
    user = {
        "id": payload.get("sub"),
        "email": payload.get("email"),
        "role": payload.get("role"),
    }

    if not user["id"]:
        raise HTTPException(status_code=401, detail="Invalid user ID in token")

    return user


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> str:
    """Get current user ID from JWT token."""
    user = await get_current_user(credentials)
    return user["id"]


ADMIN_EMAILS = {e.strip() for e in settings.admin_emails.split(",") if e.strip()}


async def require_admin(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> Dict[str, Any]:
    """Require admin access. Returns user if admin, raises 403 otherwise."""
    user = await get_current_user(credentials)
    if user["email"] not in ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
