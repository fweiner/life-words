"""Life Words service for managing contacts, items, sessions, and progress."""
import random
from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from app.core.database import SupabaseClient
from app.models.life_words import (
    PersonalContactCreate,
    PersonalContactUpdate,
    QuickAddContactCreate,
    LifeWordsSessionCreate,
    LifeWordsResponseCreate,
)
from app.services.utils import (
    empty_to_none,
    verify_ownership,
    verify_session,
    build_update_data,
    soft_delete_entity,
    list_user_entities,
)

MIN_CONTACTS_REQUIRED = 2
MAX_SESSION_ENTRIES = 6
CONTACTS_TABLE = "personal_contacts"
ITEMS_TABLE = "personal_items"
SESSIONS_TABLE = "life_words_sessions"


def convert_items_to_contacts(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert personal items to contact-like format for unified session handling."""
    result = []
    for item in items:
        result.append({
            "id": item["id"],
            "name": item["name"],
            "nickname": None,
            "relationship": "item",
            "photo_url": item["photo_url"],
            "first_letter": item["name"][0].upper() if item["name"] else None,
            "category": item.get("category"),
            "description": item.get("purpose"),
            "association": item.get("associated_with"),
            "location_context": item.get("location"),
            "item_features": item.get("features"),
            "item_size": item.get("size"),
            "item_shape": item.get("shape"),
            "item_color": item.get("color"),
            "item_weight": item.get("weight"),
        })
    return result


class LifeWordsService:
    """Service for Life Words treatment operations."""

    def __init__(self, db: SupabaseClient):
        self.db = db

    async def get_status(self, user_id: str) -> Dict[str, Any]:
        """Get user's life words setup status (counts complete contacts + items)."""
        contacts = await self.db.query(
            CONTACTS_TABLE,
            select="id",
            filters={"user_id": user_id, "is_active": True, "is_complete": True}
        )
        items = await self.db.query(
            ITEMS_TABLE,
            select="id",
            filters={"user_id": user_id, "is_active": True, "is_complete": True}
        )

        contact_count = len(contacts) if contacts else 0
        item_count = len(items) if items else 0
        total_count = contact_count + item_count

        return {
            "contact_count": contact_count,
            "item_count": item_count,
            "total_count": total_count,
            "can_start_session": total_count >= MIN_CONTACTS_REQUIRED,
            "min_contacts_required": MIN_CONTACTS_REQUIRED,
        }

    # ---- Contact CRUD ----

    async def create_contact(
        self, user_id: str, contact_data: PersonalContactCreate
    ) -> Dict[str, Any]:
        """Create a new personal contact."""
        contact = await self.db.insert(
            CONTACTS_TABLE,
            {
                "user_id": user_id,
                "name": contact_data.name,
                "nickname": empty_to_none(contact_data.nickname),
                "pronunciation": empty_to_none(contact_data.pronunciation),
                "relationship": contact_data.relationship,
                "photo_url": contact_data.photo_url,
                "category": empty_to_none(contact_data.category),
                "description": empty_to_none(contact_data.description),
                "association": empty_to_none(contact_data.association),
                "location_context": empty_to_none(contact_data.location_context),
                "interests": empty_to_none(contact_data.interests),
                "personality": empty_to_none(contact_data.personality),
                "values": empty_to_none(contact_data.values),
                "social_behavior": empty_to_none(contact_data.social_behavior),
            }
        )
        return contact[0]

    async def quick_add_contact(
        self, user_id: str, data: QuickAddContactCreate
    ) -> Dict[str, Any]:
        """Quick add a contact with just a photo (incomplete draft)."""
        contact = await self.db.insert(
            CONTACTS_TABLE,
            {
                "user_id": user_id,
                "name": "",
                "relationship": "",
                "photo_url": data.photo_url,
                "category": data.category,
            }
        )
        return contact[0]

    async def list_contacts(
        self, user_id: str, include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        """List user's personal contacts."""
        return await list_user_entities(self.db, CONTACTS_TABLE, user_id, include_inactive)

    async def get_contact(self, contact_id: str, user_id: str) -> Dict[str, Any]:
        """Get a specific personal contact."""
        contacts = await self.db.query(
            CONTACTS_TABLE,
            select="*",
            filters={"id": contact_id, "user_id": user_id}
        )
        if not contacts:
            raise HTTPException(status_code=404, detail="Contact not found")
        return contacts[0]

    async def update_contact(
        self, contact_id: str, user_id: str, contact_data: PersonalContactUpdate
    ) -> Dict[str, Any]:
        """Update a personal contact."""
        await verify_ownership(self.db, CONTACTS_TABLE, contact_id, user_id, "Contact")
        update_data = build_update_data(contact_data)

        updated = await self.db.update(
            CONTACTS_TABLE,
            {"id": contact_id},
            update_data
        )
        return updated[0] if isinstance(updated, list) else updated

    async def delete_contact(self, contact_id: str, user_id: str) -> Dict[str, Any]:
        """Soft delete a personal contact."""
        return await soft_delete_entity(self.db, CONTACTS_TABLE, contact_id, user_id, "Contact")

    # ---- Sessions ----

    async def create_session(
        self, user_id: str, session_data: LifeWordsSessionCreate
    ) -> Dict[str, Any]:
        """Create a new life words session including contacts and items."""
        category = session_data.category
        contacts: List[Dict[str, Any]] = []
        items_as_contacts: List[Dict[str, Any]] = []

        # Fetch contacts unless filtering to items only
        if category != "items":
            if session_data.contact_ids:
                contacts = await self.db.query(
                    CONTACTS_TABLE,
                    select="*",
                    filters={"user_id": user_id, "is_active": True, "is_complete": True}
                )
                contacts = [c for c in contacts if c["id"] in session_data.contact_ids]
            else:
                contacts = await self.db.query(
                    CONTACTS_TABLE,
                    select="*",
                    filters={"user_id": user_id, "is_active": True, "is_complete": True}
                )
            contacts = contacts or []

        # Fetch items unless filtering to people only
        if category != "people":
            items = await self.db.query(
                ITEMS_TABLE,
                select="*",
                filters={"user_id": user_id, "is_active": True, "is_complete": True}
            )
            items_as_contacts = convert_items_to_contacts(items or [])

        all_entries = contacts + items_as_contacts

        if not all_entries or len(all_entries) < MIN_CONTACTS_REQUIRED:
            raise HTTPException(
                status_code=400,
                detail=f"At least {MIN_CONTACTS_REQUIRED} contacts or items required to start a session"
            )

        random.shuffle(all_entries)
        all_entries = all_entries[:MAX_SESSION_ENTRIES]

        contact_ids = [c["id"] for c in all_entries]

        session = await self.db.insert(
            SESSIONS_TABLE,
            {
                "user_id": user_id,
                "contact_ids": contact_ids,
                "is_completed": False,
            }
        )

        return {"session": session[0], "contacts": all_entries}

    async def get_session(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """Get session details with contacts, items, and responses."""
        session = await verify_session(self.db, SESSIONS_TABLE, session_id, user_id)
        session_ids = session["contact_ids"]

        contacts = await self.db.query(
            CONTACTS_TABLE, select="*", filters={"user_id": user_id}
        )
        session_contacts = [c for c in (contacts or []) if c["id"] in session_ids]

        items = await self.db.query(
            ITEMS_TABLE, select="*", filters={"user_id": user_id}
        )
        items_in_session = [i for i in (items or []) if i["id"] in session_ids]
        items_as_contacts = convert_items_to_contacts(items_in_session)

        all_entries = session_contacts + items_as_contacts

        responses = await self.db.query(
            "life_words_responses",
            select="*",
            filters={"session_id": session_id},
            order="completed_at.asc"
        )

        return {
            "session": session,
            "contacts": all_entries,
            "responses": responses or [],
        }

    async def save_response(
        self, session_id: str, user_id: str, response_data: LifeWordsResponseCreate
    ) -> Dict[str, Any]:
        """Save a response for a contact in a session."""
        await verify_session(self.db, SESSIONS_TABLE, session_id, user_id)

        response = await self.db.insert(
            "life_words_responses",
            {
                "session_id": session_id,
                "contact_id": response_data.contact_id,
                "user_id": user_id,
                "is_correct": response_data.is_correct,
                "cues_used": response_data.cues_used,
                "response_time": response_data.response_time,
                "user_answer": response_data.user_answer,
                "correct_answer": response_data.correct_answer,
                "speech_confidence": response_data.speech_confidence,
            }
        )
        return {"response": response[0]}

    async def complete_session(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """Mark session as completed and calculate statistics."""
        await verify_session(self.db, SESSIONS_TABLE, session_id, user_id)

        responses = await self.db.query(
            "life_words_responses",
            select="*",
            filters={"session_id": session_id}
        )
        if not responses:
            raise HTTPException(status_code=400, detail="No responses found")

        total_correct = sum(1 for r in responses if r["is_correct"])
        total_incorrect = len(responses) - total_correct
        avg_cues = sum(r["cues_used"] for r in responses) / len(responses)
        avg_time = sum(float(r["response_time"] or 0) for r in responses) / len(responses)

        statistics = {
            "responses_count": len(responses),
            "accuracy_percentage": round((total_correct / len(responses)) * 100, 1),
            "by_contact": {}
        }
        for r in responses:
            contact_id = r["contact_id"]
            if contact_id not in statistics["by_contact"]:
                statistics["by_contact"][contact_id] = {
                    "is_correct": r["is_correct"],
                    "cues_used": r["cues_used"],
                    "response_time": float(r["response_time"] or 0),
                }

        updated = await self.db.update(
            SESSIONS_TABLE,
            {"id": session_id},
            {
                "is_completed": True,
                "completed_at": "now()",
                "total_correct": total_correct,
                "total_incorrect": total_incorrect,
                "average_cues_used": round(avg_cues, 2),
                "average_response_time": round(avg_time, 2),
                "statistics": statistics,
            }
        )
        return {"session": updated}

    # ---- Progress ----

    async def get_progress(self, user_id: str) -> Dict[str, Any]:
        """Get user's life words progress statistics across all session types."""
        name_sessions = await self.db.query(
            SESSIONS_TABLE,
            select="*",
            filters={"user_id": user_id, "is_completed": True},
            order="completed_at.desc"
        )
        question_sessions = await self.db.query(
            "life_words_question_sessions",
            select="*",
            filters={"user_id": user_id, "is_completed": True},
            order="completed_at.desc"
        )
        info_sessions = await self.db.query(
            "life_words_information_sessions",
            select="*",
            filters={"user_id": user_id, "is_completed": True},
            order="completed_at.desc"
        )

        name_responses = await self.db.query(
            "life_words_responses", select="*", filters={"user_id": user_id}
        )
        question_responses = await self.db.query(
            "life_words_question_responses", select="*", filters={"user_id": user_id}
        )
        info_responses = await self.db.query(
            "life_words_information_responses", select="*", filters={"user_id": user_id}
        )

        total_name_sessions = len(name_sessions) if name_sessions else 0
        total_question_sessions = len(question_sessions) if question_sessions else 0
        total_info_sessions = len(info_sessions) if info_sessions else 0

        name_correct = sum(1 for r in (name_responses or []) if r.get("is_correct"))
        name_total = len(name_responses) if name_responses else 0
        question_correct = sum(1 for r in (question_responses or []) if r.get("is_correct"))
        question_total = len(question_responses) if question_responses else 0
        info_correct = sum(1 for r in (info_responses or []) if r.get("is_correct"))
        info_total = len(info_responses) if info_responses else 0

        def _avg(values):
            return round(sum(values) / len(values), 1) if values else 0

        name_response_times = [
            float(r.get("response_time") or 0)
            for r in (name_responses or []) if r.get("response_time")
        ]
        question_response_times = [
            float(r.get("response_time") or 0)
            for r in (question_responses or []) if r.get("response_time")
        ]
        question_clarity_scores = [
            float(r.get("clarity_score") or 0)
            for r in (question_responses or []) if r.get("clarity_score") is not None
        ]
        name_confidence_scores = [
            float(r.get("speech_confidence") or 0)
            for r in (name_responses or []) if r.get("speech_confidence") is not None
        ]
        info_response_times = [
            float(r.get("response_time") or 0)
            for r in (info_responses or []) if r.get("response_time")
        ]
        info_hints_used = [
            1 if r.get("used_hint") else 0 for r in (info_responses or [])
        ]

        # Build session history
        session_history = []
        for s in (name_sessions or [])[:15]:
            tc = s.get("total_correct", 0)
            ti = s.get("total_incorrect", 0)
            session_history.append({
                "type": "name",
                "date": s.get("completed_at"),
                "total_correct": tc,
                "total_incorrect": ti,
                "accuracy": round((tc / max(1, tc + ti)) * 100, 1),
                "avg_response_time": s.get("average_response_time", 0),
                "avg_cues_used": s.get("average_cues_used", 0),
            })
        for s in (question_sessions or [])[:15]:
            tc = s.get("total_correct", 0)
            tq = s.get("total_questions", 5)
            session_history.append({
                "type": "question",
                "date": s.get("completed_at"),
                "total_correct": tc,
                "total_questions": tq,
                "accuracy": round((tc / max(1, tq)) * 100, 1),
                "avg_response_time": s.get("average_response_time", 0),
                "avg_clarity": s.get("average_clarity_score", 0),
            })
        for s in (info_sessions or [])[:15]:
            tc = s.get("total_correct", 0)
            tq = s.get("total_questions", 5)
            session_history.append({
                "type": "information",
                "date": s.get("completed_at"),
                "total_correct": tc,
                "total_questions": tq,
                "accuracy": round((tc / max(1, tq)) * 100, 1),
                "avg_response_time": s.get("average_response_time", 0),
                "hints_used": s.get("hints_used", 0),
            })

        session_history.sort(key=lambda x: x.get("date") or "", reverse=True)

        return {
            "summary": {
                "total_sessions": total_name_sessions + total_question_sessions + total_info_sessions,
                "name_practice": {
                    "sessions": total_name_sessions,
                    "correct": name_correct,
                    "total": name_total,
                    "accuracy": round((name_correct / max(1, name_total)) * 100, 1),
                    "avg_response_time_sec": _avg(name_response_times),
                    "avg_speech_confidence": round(
                        sum(name_confidence_scores) / len(name_confidence_scores) * 100, 1
                    ) if name_confidence_scores else 0,
                },
                "question_practice": {
                    "sessions": total_question_sessions,
                    "correct": question_correct,
                    "total": question_total,
                    "accuracy": round((question_correct / max(1, question_total)) * 100, 1),
                    "avg_response_time_ms": _avg(question_response_times),
                    "avg_clarity": round(
                        sum(question_clarity_scores) / len(question_clarity_scores) * 100, 1
                    ) if question_clarity_scores else 0,
                },
                "information_practice": {
                    "sessions": total_info_sessions,
                    "correct": info_correct,
                    "total": info_total,
                    "accuracy": round((info_correct / max(1, info_total)) * 100, 1),
                    "avg_response_time_sec": _avg(info_response_times),
                    "hint_rate": round(
                        sum(info_hints_used) / len(info_hints_used) * 100, 1
                    ) if info_hints_used else 0,
                },
            },
            "session_history": session_history[:20],
        }
