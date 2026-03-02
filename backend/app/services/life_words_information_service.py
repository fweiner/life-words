"""Life Words Information Practice service."""
import random
from datetime import datetime, timezone
from typing import List, Dict, Any
from fastapi import HTTPException
from app.core.database import SupabaseClient
from app.services.utils import verify_session, verify_can_practice, get_profile_or_404, calculate_session_accuracy
from app.models.life_words_information import (
    InformationItem,
    LifeWordsInformationResponseCreate,
)

MIN_FIELDS_REQUIRED = 5

# Profile fields that can be practiced
PRACTICE_FIELDS = {
    "phone_number": {
        "label": "phone number",
        "teach_template": "Your phone number is {value}",
        "question": "What is your phone number?",
        "hint_type": "first_digit",
    },
    "address_city": {
        "label": "city",
        "teach_template": "You live in {value}",
        "question": "What city do you live in?",
        "hint_type": "first_letter",
    },
    "address_state": {
        "label": "state",
        "teach_template": "You live in the state of {value}",
        "question": "What state do you live in?",
        "hint_type": "first_letter",
    },
    "address_zip": {
        "label": "zip code",
        "teach_template": "Your zip code is {value}",
        "question": "What is your zip code?",
        "hint_type": "first_digit",
    },
    "date_of_birth": {
        "label": "birthday",
        "teach_template": "Your birthday is {value}",
        "question": "When is your birthday?",
        "hint_type": "first_letter",
    },
    "full_name": {
        "label": "full name",
        "teach_template": "Your full name is {value}",
        "question": "What is your full name?",
        "hint_type": "first_letter",
    },
    "job": {
        "label": "job",
        "teach_template": "Your job is {value}",
        "question": "What is your job?",
        "hint_type": "first_letter",
    },
    "marital_status": {
        "label": "marital status",
        "teach_template": "Your marital status is {value}",
        "question": "What is your marital status?",
        "hint_type": "first_letter",
    },
    "number_of_children": {
        "label": "number of children",
        "teach_template": "You have {value} children",
        "question": "How many children do you have?",
        "hint_type": "first_digit",
    },
    "favorite_food": {
        "label": "favorite food",
        "teach_template": "Your favorite food is {value}",
        "question": "What is your favorite food?",
        "hint_type": "first_letter",
    },
    "favorite_music": {
        "label": "favorite music",
        "teach_template": "Your favorite music is {value}",
        "question": "What is your favorite music?",
        "hint_type": "first_letter",
    },
    "hair_color": {
        "label": "hair color",
        "teach_template": "Your hair color is {value}",
        "question": "What is your hair color?",
        "hint_type": "first_letter",
    },
    "eye_color": {
        "label": "eye color",
        "teach_template": "Your eye color is {value}",
        "question": "What is your eye color?",
        "hint_type": "first_letter",
    },
}

STATE_ABBREVIATIONS = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming", "DC": "District of Columbia",
}


def format_phone_for_tts(phone: str) -> str:
    """Format phone number for TTS to read digits individually."""
    digits = ''.join(c for c in str(phone) if c.isdigit())
    if len(digits) == 10:
        return f"{digits[0]} {digits[1]} {digits[2]}, {digits[3]} {digits[4]} {digits[5]}, {digits[6]} {digits[7]} {digits[8]} {digits[9]}"
    elif len(digits) == 7:
        return f"{digits[0]} {digits[1]} {digits[2]}, {digits[3]} {digits[4]} {digits[5]} {digits[6]}"
    else:
        return ' '.join(digits)


def format_zip_for_tts(zip_code: str) -> str:
    """Format zip code for TTS to read digits individually."""
    digits = ''.join(c for c in str(zip_code) if c.isdigit())
    return ' '.join(digits)


def format_state_for_tts(state: str) -> str:
    """Expand state abbreviation to full name for TTS."""
    state_upper = str(state).strip().upper()
    return STATE_ABBREVIATIONS.get(state_upper, state)


def format_date_for_display(date_value) -> str:
    """Format a date value for display."""
    if date_value is None:
        return ""
    if isinstance(date_value, str):
        try:
            from datetime import datetime as dt
            parsed = dt.fromisoformat(date_value.replace("Z", "+00:00"))
            return parsed.strftime("%B %d")
        except (ValueError, AttributeError) as e:
            from app.core.error_logger import log_error
            log_error(
                error=e,
                source="swallowed",
                service_name="life_words_information_service",
                function_name="format_date_for_display",
            )
            return date_value
    if hasattr(date_value, "strftime"):
        return date_value.strftime("%B %d")
    return str(date_value)


def generate_hint(value: str, hint_type: str) -> str:
    """Generate a hint based on the value and hint type."""
    if not value:
        return ""

    value_str = str(value).strip()

    if hint_type == "first_letter":
        first_char = value_str[0].upper() if value_str else ""
        return f"It starts with the letter {first_char}"
    elif hint_type == "first_digit":
        for char in value_str:
            if char.isdigit():
                return f"The first digit is {char}"
        first_char = value_str[0] if value_str else ""
        return f"It starts with {first_char}"

    return f"The first character is {value_str[0] if value_str else ''}"


def get_filled_fields_count(profile: Dict[str, Any]) -> int:
    """Count how many practice fields are filled in the profile."""
    count = 0
    for field_name in PRACTICE_FIELDS.keys():
        value = profile.get(field_name)
        if value is not None and str(value).strip():
            count += 1
    return count


def generate_information_items(profile: Dict[str, Any]) -> List[InformationItem]:
    """Generate up to 5 information items from the user's profile."""
    items = []

    filled_fields = []
    for field_name, config in PRACTICE_FIELDS.items():
        value = profile.get(field_name)
        if value is not None and str(value).strip():
            filled_fields.append((field_name, config, value))

    random.shuffle(filled_fields)
    selected = filled_fields[:5]

    for field_name, config, value in selected:
        if field_name == "date_of_birth":
            display_value = format_date_for_display(value)
        elif field_name == "number_of_children":
            display_value = str(value)
        else:
            display_value = str(value)

        if field_name == "phone_number":
            tts_value = format_phone_for_tts(value)
        elif field_name == "address_zip":
            tts_value = format_zip_for_tts(value)
        elif field_name == "address_state":
            tts_value = format_state_for_tts(value)
        elif field_name == "full_name":
            pronunciation = profile.get("full_name_pronunciation")
            tts_value = pronunciation if pronunciation and str(pronunciation).strip() else display_value
        else:
            tts_value = display_value

        hint_value = display_value
        if field_name == "date_of_birth":
            hint_value = display_value.split()[0] if display_value else ""
        hint_text = generate_hint(hint_value, config["hint_type"])

        items.append(InformationItem(
            field_name=field_name,
            field_label=config["label"],
            teach_text=config["teach_template"].format(value=tts_value),
            question_text=config["question"],
            expected_answer=display_value,
            hint_text=hint_text,
        ))

    return items


class LifeWordsInformationService:
    """Service for Life Words Information Practice sessions."""

    def __init__(self, db: SupabaseClient):
        self.db = db

    async def get_information_status(self, user_id: str) -> Dict[str, Any]:
        """Check if user has enough profile data for information practice."""
        profiles = await self.db.query(
            "profiles", select="*", filters={"id": user_id}
        )

        if not profiles:
            return {
                "can_start_session": False,
                "filled_fields_count": 0,
                "min_fields_required": MIN_FIELDS_REQUIRED,
            }

        profile = profiles[0]  # Intentionally not using get_profile_or_404 here — returns zeroed status instead
        filled_count = get_filled_fields_count(profile)

        return {
            "can_start_session": filled_count >= MIN_FIELDS_REQUIRED,
            "filled_fields_count": filled_count,
            "min_fields_required": MIN_FIELDS_REQUIRED,
        }

    async def create_session(self, user_id: str) -> Dict[str, Any]:
        """Create a new information practice session with up to 5 random items."""
        await verify_can_practice(self.db, user_id)

        profile = await get_profile_or_404(self.db, user_id)
        filled_count = get_filled_fields_count(profile)
        if filled_count < MIN_FIELDS_REQUIRED:
            raise HTTPException(
                status_code=400,
                detail=f"At least {MIN_FIELDS_REQUIRED} profile fields required. You have {filled_count}."
            )

        items = generate_information_items(profile)
        if len(items) < 1:
            raise HTTPException(
                status_code=400,
                detail="Not enough profile data to generate practice items"
            )

        session = await self.db.insert(
            "life_words_information_sessions",
            {
                "user_id": user_id,
                "is_completed": False,
                "total_items": len(items),
                "total_correct": 0,
                "total_hints_used": 0,
                "total_timeouts": 0,
                "average_response_time": 0,
            }
        )

        return {
            "session": session[0],
            "items": [item.model_dump() for item in items],
        }

    async def get_session(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """Get information session with responses."""
        session = await verify_session(
            self.db, "life_words_information_sessions", session_id, user_id
        )

        responses = await self.db.query(
            "life_words_information_responses",
            select="*",
            filters={"session_id": session_id},
            order="created_at"
        )

        return {"session": session, "responses": responses or []}

    async def save_response(
        self, session_id: str, user_id: str,
        response_data: LifeWordsInformationResponseCreate
    ) -> Dict[str, Any]:
        """Save a response to an information item."""
        await verify_session(
            self.db, "life_words_information_sessions", session_id, user_id
        )

        response = await self.db.insert(
            "life_words_information_responses",
            {
                "session_id": session_id,
                "user_id": user_id,
                "field_name": response_data.field_name,
                "field_label": response_data.field_label,
                "teach_text": response_data.teach_text,
                "question_text": response_data.question_text,
                "expected_answer": response_data.expected_answer,
                "hint_text": response_data.hint_text,
                "user_answer": response_data.user_answer,
                "is_correct": response_data.is_correct,
                "used_hint": response_data.used_hint,
                "timed_out": response_data.timed_out,
                "response_time": response_data.response_time,
            }
        )
        return {"response": response[0]}

    async def complete_session(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """Complete an information session and calculate statistics."""
        await verify_session(
            self.db, "life_words_information_sessions", session_id, user_id
        )

        responses = await self.db.query(
            "life_words_information_responses",
            select="*",
            filters={"session_id": session_id}
        )
        total_correct, accuracy_pct = calculate_session_accuracy(responses)
        total_hints_used = sum(1 for r in responses if r["used_hint"]) if responses else 0
        total_timeouts = sum(1 for r in responses if r["timed_out"]) if responses else 0

        response_times = [r["response_time"] for r in responses if r["response_time"]]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        statistics = {
            "total_items": len(responses) if responses else 0,
            "total_correct": total_correct,
            "total_hints_used": total_hints_used,
            "total_timeouts": total_timeouts,
            "accuracy_percentage": accuracy_pct,
            "average_response_time_ms": round(avg_response_time, 0),
            "by_field": {}
        }

        for r in responses:
            field = r["field_name"]
            statistics["by_field"][field] = {
                "is_correct": r["is_correct"],
                "used_hint": r["used_hint"],
                "timed_out": r["timed_out"],
                "response_time": r["response_time"],
            }

        updated = await self.db.update(
            "life_words_information_sessions",
            {"id": session_id},
            {
                "is_completed": True,
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "total_correct": total_correct,
                "total_hints_used": total_hints_used,
                "total_timeouts": total_timeouts,
                "average_response_time": round(avg_response_time, 2),
                "statistics": statistics,
            }
        )

        return {"session": updated, "statistics": statistics}
