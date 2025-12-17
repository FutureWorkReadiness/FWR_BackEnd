"""
Badge and UserBadge models.
Defines microcredentials/badges that users can earn.
"""

import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Text, Float, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.app.db.base import Base


class Badge(Base):
    """
    Microcredentials and badges that users can earn.
    Badges are awarded based on reaching certain score thresholds.
    """

    __tablename__ = "badges"

    badge_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(200), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    criteria = Column(Text, nullable=False)  # JSON string describing earning criteria
    icon_url = Column(String(500), nullable=True)  # URL to badge icon
    category = Column(String(50), nullable=False)  # 'readiness', 'technical', 'soft_skills', 'leadership'
    required_score = Column(Float, nullable=False)  # Minimum score required to earn
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user_badges = relationship("UserBadge", back_populates="badge", cascade="all, delete-orphan")


class UserBadge(Base):
    """
    Tracks which badges a user has earned.
    Junction table between User and Badge.
    """

    __tablename__ = "user_badges"

    user_badge_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    badge_id = Column(UUID(as_uuid=True), ForeignKey("badges.badge_id"), nullable=False)
    earned_date = Column(DateTime(timezone=True), server_default=func.now())
    shared = Column(Boolean, default=False)  # Whether user has shared this badge

    # Relationships
    user = relationship("User", back_populates="user_badges")
    badge = relationship("Badge", back_populates="user_badges")

    # Unique constraint to prevent duplicate badges per user
    __table_args__ = (
        UniqueConstraint("user_id", "badge_id", name="unique_user_badge"),
    )

