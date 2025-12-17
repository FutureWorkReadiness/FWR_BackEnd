"""
User model.
Defines user accounts, profiles, and score tracking.
"""

import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.app.db.base import Base


class User(Base):
    """
    User accounts and profiles.
    Tracks user information, specialization preference, and readiness scores.
    """

    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Profile information
    preferred_specialization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("specializations.specialization_id"),
        nullable=True,
    )

    # Scores and progress
    readiness_score = Column(Float, default=0.0)
    technical_score = Column(Float, default=0.0)
    soft_skills_score = Column(Float, default=0.0)
    leadership_score = Column(Float, default=0.0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    preferred_specialization = relationship("Specialization")
    quiz_attempts = relationship("QuizAttempt", back_populates="user", cascade="all, delete-orphan")
    user_badges = relationship("UserBadge", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    journal_entries = relationship("JournalEntry", back_populates="user", cascade="all, delete-orphan")

