"""
User schemas.
Pydantic models for user authentication and profile.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    """Base schema for User data."""

    email: str
    name: str


class UserCreate(UserBase):
    """Schema for user registration."""

    password: str


class UserLogin(BaseModel):
    """Schema for user login."""

    email: str
    password: str


class User(UserBase):
    """Schema for User response."""

    user_id: UUID
    preferred_specialization_id: Optional[UUID] = None
    readiness_score: Optional[float] = None
    technical_score: Optional[float] = None
    soft_skills_score: Optional[float] = None
    leadership_score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user profile."""

    preferred_specialization_id: Optional[UUID] = None


class UserResponse(BaseModel):
    """Response schema for user operations."""

    success: bool
    user: User


class LoginResponse(BaseModel):
    """Response schema for login."""

    success: bool
    user: User

