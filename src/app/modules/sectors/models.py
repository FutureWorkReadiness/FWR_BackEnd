"""
Sector, Branch, and Specialization models.
Defines the hierarchical industry structure: Sector → Branch → Specialization
"""

import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.app.db.base import Base


class Sector(Base):
    """
    Main sectors (e.g., Technology, Healthcare, etc.)
    Top level of the industry hierarchy.
    """

    __tablename__ = "sectors"

    sector_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    branches = relationship("Branch", back_populates="sector", cascade="all, delete-orphan")


class Branch(Base):
    """
    Branches within sectors (e.g., Software Development & Engineering under Technology)
    Second level of the industry hierarchy.
    """

    __tablename__ = "branches"

    branch_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(150), nullable=False, index=True)
    description = Column(Text, nullable=True)
    sector_id = Column(UUID(as_uuid=True), ForeignKey("sectors.sector_id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    sector = relationship("Sector", back_populates="branches")
    specializations = relationship("Specialization", back_populates="branch", cascade="all, delete-orphan")


class Specialization(Base):
    """
    Specializations within branches (e.g., Frontend Development under Software Development)
    Third level of the industry hierarchy. Users select a specialization and take quizzes.
    """

    __tablename__ = "specializations"

    specialization_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(150), nullable=False, index=True)
    description = Column(Text, nullable=True)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.branch_id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    branch = relationship("Branch", back_populates="specializations")
    quizzes = relationship("Quiz", back_populates="specialization", cascade="all, delete-orphan")

