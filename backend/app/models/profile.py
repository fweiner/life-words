"""Profile-related Pydantic models."""
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel


class ProfileUpdate(BaseModel):
    """Profile update request."""
    full_name: Optional[str] = None
    full_name_pronunciation: Optional[str] = None
    date_of_birth: Optional[date] = None
    # Personal information fields
    gender: Optional[str] = None
    height: Optional[str] = None
    weight: Optional[str] = None
    hair_color: Optional[str] = None
    eye_color: Optional[str] = None
    job: Optional[str] = None
    phone_number: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_zip: Optional[str] = None
    marital_status: Optional[str] = None
    number_of_children: Optional[int] = None
    favorite_food: Optional[str] = None
    favorite_music: Optional[str] = None
    # Voice preference
    voice_gender: Optional[str] = None  # 'male', 'female', or 'neutral'
    # Answer matching accommodations
    match_acceptable_alternatives: Optional[bool] = None
    match_partial_substring: Optional[bool] = None
    match_word_overlap: Optional[bool] = None
    match_stop_word_filtering: Optional[bool] = None
    match_synonyms: Optional[bool] = None
    match_first_name_only: Optional[bool] = None


class ProfileResponse(BaseModel):
    """Profile response."""
    id: str
    email: str
    full_name: Optional[str] = None
    full_name_pronunciation: Optional[str] = None
    date_of_birth: Optional[date] = None
    # Personal information fields
    gender: Optional[str] = None
    height: Optional[str] = None
    weight: Optional[str] = None
    hair_color: Optional[str] = None
    eye_color: Optional[str] = None
    job: Optional[str] = None
    phone_number: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_zip: Optional[str] = None
    marital_status: Optional[str] = None
    number_of_children: Optional[int] = None
    favorite_food: Optional[str] = None
    favorite_music: Optional[str] = None
    # Voice preference
    voice_gender: Optional[str] = None  # 'male', 'female', or 'neutral'
    # Answer matching accommodations
    match_acceptable_alternatives: Optional[bool] = True
    match_partial_substring: Optional[bool] = True
    match_word_overlap: Optional[bool] = True
    match_stop_word_filtering: Optional[bool] = True
    match_synonyms: Optional[bool] = True
    match_first_name_only: Optional[bool] = True
    created_at: datetime
    updated_at: datetime
