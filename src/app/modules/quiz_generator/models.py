"""
Quiz Generator models.
Stores generation job tracking for async quiz generation tasks.
"""

import uuid
from sqlalchemy import Column, String, Text, DateTime, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from src.app.db.base import Base


class GenerationJob(Base):
    """
    Generation Job model.
    Tracks quiz generation tasks initiated via API.
    """

    __tablename__ = "generation_jobs"

    # Primary key
    job_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    # Job type: 'full', 'sector', 'career_level', 'soft_skills', 'status_check'
    job_type = Column(String(50), nullable=False, index=True)

    # Status: 'pending', 'running', 'completed', 'failed', 'cancelled'
    status = Column(String(20), nullable=False, default="pending", index=True)

    # Job parameters (sector, career, level, etc.)
    parameters = Column(JSON, nullable=True)

    # Progress tracking
    progress_percent = Column(Integer, default=0)
    progress_message = Column(String(500), nullable=True)

    # Results summary (on completion)
    result_summary = Column(JSON, nullable=True)

    # Error message (on failure)
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<GenerationJob(job_id={self.job_id}, type={self.job_type}, status={self.status})>"

