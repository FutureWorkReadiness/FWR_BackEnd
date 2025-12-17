"""
Goal and JournalEntry models.
Defines user goals for tracking progress and journal entries for reflection.
"""

import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Text, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.app.db.base import Base


class Goal(Base):
    """
    User goals for tracking progress.
    Goals are linked to score categories and auto-update as user takes quizzes.
    """

    __tablename__ = "goals"

    goal_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)  # 'readiness', 'technical', 'soft_skills', 'leadership'
    target_value = Column(Float, nullable=False)
    current_value = Column(Float, default=0.0)
    is_completed = Column(Boolean, default=False)
    target_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="goals")


class JournalEntry(Base):
    """
    User journal entries for reflection.
    Users can write about their learning journey and progress.
    """

    __tablename__ = "journal_entries"

    entry_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    content = Column(Text, nullable=False)
    prompt = Column(String(500), nullable=True)  # Optional writing prompt
    entry_date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="journal_entries")

