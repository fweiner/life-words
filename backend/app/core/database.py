"""Database client for Supabase using httpx."""
import httpx
from typing import Optional, Dict, Any, List
from app.config import settings


class SupabaseClient:
    """Client for interacting with Supabase REST API."""

    def __init__(self):
        self.url = settings.supabase_url
        self.key = settings.supabase_secret_key
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

    async def query(
        self,
        table: str,
        select: str = "*",
        filters: Optional[Dict[str, Any]] = None,
        order: Optional[str] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Query table with filters."""
        url = f"{self.url}/rest/v1/{table}"
        params = {"select": select}

        if filters:
            for key, value in filters.items():
                params[f"{key}"] = f"eq.{value}"

        # Support both 'order' and 'order_by' parameter names
        order_field = order or order_by
        if order_field:
            if order_desc:
                params["order"] = f"{order_field}.desc"
            else:
                params["order"] = order_field

        if limit:
            params["limit"] = str(limit)

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()

    async def insert(
        self,
        table: str,
        data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Insert a row into table."""
        url = f"{self.url}/rest/v1/{table}"

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result if isinstance(result, list) else [result]

    async def upsert(
        self,
        table: str,
        data: Dict[str, Any],
        on_conflict: str = ""
    ) -> List[Dict[str, Any]]:
        """Insert or update a row (merge on conflict)."""
        url = f"{self.url}/rest/v1/{table}"
        headers = {**self.headers, "Prefer": "return=representation,resolution=merge-duplicates"}
        params = {}
        if on_conflict:
            params["on_conflict"] = on_conflict

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data, params=params)
            response.raise_for_status()
            result = response.json()
            return result if isinstance(result, list) else [result]

    async def update(
        self,
        table: str,
        filters: Dict[str, Any],
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update rows in table."""
        url = f"{self.url}/rest/v1/{table}"
        params = {}

        for key, value in filters.items():
            params[f"{key}"] = f"eq.{value}"

        async with httpx.AsyncClient() as client:
            response = await client.patch(
                url, headers=self.headers, params=params, json=data
            )
            response.raise_for_status()
            result = response.json()
            if isinstance(result, list):
                return result[0] if result else {}
            return result

    async def delete(
        self,
        table: str,
        filters: Dict[str, Any]
    ) -> bool:
        """Delete rows from table."""
        url = f"{self.url}/rest/v1/{table}"
        params = {}

        for key, value in filters.items():
            params[f"{key}"] = f"eq.{value}"

        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=self.headers, params=params)
            response.raise_for_status()
            return True

    async def rpc(
        self,
        function_name: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Call a Supabase RPC function."""
        url = f"{self.url}/rest/v1/rpc/{function_name}"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url, headers=self.headers, json=params or {}
            )
            response.raise_for_status()
            return response.json()


# Global database client instance
db = SupabaseClient()
