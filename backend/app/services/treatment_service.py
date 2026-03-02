"""Treatment service for managing treatment sessions and results."""
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.core.database import SupabaseClient
from app.models.schemas import (
    TreatmentSessionCreate,
    TreatmentSessionResponse,
    TreatmentResultCreate,
    TreatmentResultResponse,
    UserProgressResponse
)


class TreatmentService:
    """Service for treatment sessions and results."""

    def __init__(self, db: SupabaseClient):
        self.db = db

    async def create_session(
        self,
        user_id: str,
        session_data: TreatmentSessionCreate
    ) -> Dict[str, Any]:
        """Create a new treatment session."""
        data = {
            "user_id": user_id,
            "treatment_type": session_data.treatment_type,
            "data": session_data.data,
            "started_at": datetime.now(timezone.utc).isoformat()
        }

        result = await self.db.insert("treatment_sessions", data)
        return result

    async def get_session(
        self,
        session_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Get a specific session. Raises 404 if not found."""
        from fastapi import HTTPException
        results = await self.db.query(
            "treatment_sessions",
            filters={"id": session_id, "user_id": user_id},
            limit=1
        )
        if not results:
            raise HTTPException(status_code=404, detail="Session not found")
        return results[0]

    async def complete_session(
        self,
        session_id: str,
        user_id: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Mark a session as completed."""
        update_data = {
            "completed_at": datetime.now(timezone.utc).isoformat()
        }
        if data:
            update_data["data"] = data

        result = await self.db.update(
            "treatment_sessions",
            filters={"id": session_id, "user_id": user_id},
            data=update_data
        )
        return result

    async def get_user_sessions(
        self,
        user_id: str,
        treatment_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get all sessions for a user."""
        filters = {"user_id": user_id}
        if treatment_type:
            filters["treatment_type"] = treatment_type

        results = await self.db.query(
            "treatment_sessions",
            filters=filters,
            order="created_at.desc",
            limit=limit
        )
        return results

    async def create_result(
        self,
        user_id: str,
        result_data: TreatmentResultCreate
    ) -> Dict[str, Any]:
        """Create a treatment result."""
        data = {
            "session_id": result_data.session_id,
            "user_id": user_id,
            "score": result_data.score,
            "details": result_data.details
        }

        result = await self.db.insert("treatment_results", data)

        # Update user progress
        await self._update_user_progress(
            user_id,
            result_data.session_id
        )

        return result

    async def get_user_results(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get all results for a user."""
        results = await self.db.query(
            "treatment_results",
            filters={"user_id": user_id},
            order="created_at.desc",
            limit=limit
        )
        return results

    async def get_user_progress(
        self,
        user_id: str,
        treatment_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get user progress."""
        filters = {"user_id": user_id}
        if treatment_type:
            filters["treatment_type"] = treatment_type

        results = await self.db.query(
            "user_progress",
            filters=filters
        )
        return results

    async def _update_user_progress(
        self,
        user_id: str,
        session_id: str
    ) -> None:
        """Update user progress after completing a session."""
        # Get the session to find treatment type
        session_results = await self.db.query(
            "treatment_sessions",
            filters={"id": session_id, "user_id": user_id},
            limit=1
        )

        if not session_results:
            return

        session = session_results[0]
        treatment_type = session["treatment_type"]

        # Get all results for this treatment type
        results = await self.db.query(
            "treatment_results",
            select="score",
            filters={"user_id": user_id}
        )

        # Calculate statistics
        scores = [r["score"] for r in results if r.get("score") is not None]
        total_sessions = len(results)
        average_score = sum(scores) / len(scores) if scores else None

        # Check if progress record exists
        existing = await self.db.query(
            "user_progress",
            filters={"user_id": user_id, "treatment_type": treatment_type},
            limit=1
        )

        progress_data = {
            "total_sessions": total_sessions,
            "average_score": average_score,
            "last_session_at": datetime.now(timezone.utc).isoformat()
        }

        if existing:
            # Update existing record
            await self.db.update(
                "user_progress",
                filters={"user_id": user_id, "treatment_type": treatment_type},
                data=progress_data
            )
        else:
            # Create new record
            progress_data.update({
                "user_id": user_id,
                "treatment_type": treatment_type
            })
            await self.db.insert("user_progress", progress_data)
