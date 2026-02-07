"""Personal Items (My Stuff) Pydantic models."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PersonalItemCreate(BaseModel):
    """Create personal item request."""
    name: str
    pronunciation: Optional[str] = None  # How to pronounce the name
    photo_url: str
    purpose: Optional[str] = None
    features: Optional[str] = None
    category: Optional[str] = None
    size: Optional[str] = None
    shape: Optional[str] = None
    color: Optional[str] = None
    weight: Optional[str] = None
    location: Optional[str] = None
    associated_with: Optional[str] = None


class PersonalItemUpdate(BaseModel):
    """Update personal item request."""
    name: Optional[str] = None
    pronunciation: Optional[str] = None
    photo_url: Optional[str] = None
    purpose: Optional[str] = None
    features: Optional[str] = None
    category: Optional[str] = None
    size: Optional[str] = None
    shape: Optional[str] = None
    color: Optional[str] = None
    weight: Optional[str] = None
    location: Optional[str] = None
    associated_with: Optional[str] = None


class PersonalItemResponse(BaseModel):
    """Personal item response."""
    id: str
    user_id: str
    name: str
    pronunciation: Optional[str] = None
    photo_url: str
    purpose: Optional[str] = None
    features: Optional[str] = None
    category: Optional[str] = None
    size: Optional[str] = None
    shape: Optional[str] = None
    color: Optional[str] = None
    weight: Optional[str] = None
    location: Optional[str] = None
    associated_with: Optional[str] = None
    is_active: bool
    is_complete: bool = True
    created_at: datetime
    updated_at: datetime


class QuickAddItemCreate(BaseModel):
    """Quick add item - photo only, creates incomplete draft."""
    photo_url: str
