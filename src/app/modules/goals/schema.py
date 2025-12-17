"""
Goal and JournalEntry schemas.
Pydantic models for user goals and journal.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


# Goal schemas
class GoalBase(BaseModel):
    """Base schema for Goal data."""

    title: str
    description: Optional[str] = None
    category: str  # 'readiness', 'technical', 'soft_skills', 'leadership'
    target_value: float
    target_date: Optional[datetime] = None


class GoalCreate(GoalBase):
    """Schema for creating a new Goal."""

    pass


class Goal(GoalBase):
    """Schema for Goal response."""

    goal_id: UUID
    user_id: UUID
    current_value: float
    is_completed: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Journal Entry schemas
class JournalEntryBase(BaseModel):
    """Base schema for JournalEntry data."""

    content: str
    prompt: Optional[str] = None


class JournalEntryCreate(JournalEntryBase):
    """Schema for creating a new JournalEntry."""

    pass


class JournalEntry(JournalEntryBase):
    """Schema for JournalEntry response."""

    entry_id: UUID
    user_id: UUID
    entry_date: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JournalEntryUpdate(BaseModel):
    """Schema for updating a JournalEntry."""

    content: str

