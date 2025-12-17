"""
PeerBenchmark model.
Stores peer benchmarking statistics for each specialization.
"""

import uuid
from sqlalchemy import Column, Integer, DateTime, Float, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.app.db.base import Base


class PeerBenchmark(Base):
    """
    Stores peer benchmarking statistics for each specialization.
    Used to compare user scores with peers in the same specialization.
    Should be recalculated periodically (e.g., daily).
    """

    __tablename__ = "peer_benchmarks"

    benchmark_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    specialization_id = Column(
        UUID(as_uuid=True), ForeignKey("specializations.specialization_id"), nullable=False
    )

    # Average scores across all users in specialization
    avg_readiness_score = Column(Float, nullable=False, default=0.0)
    avg_technical_score = Column(Float, nullable=False, default=0.0)
    avg_soft_skills_score = Column(Float, nullable=False, default=0.0)
    avg_leadership_score = Column(Float, nullable=False, default=0.0)

    # Statistics
    total_users = Column(Integer, nullable=False, default=0)
    median_readiness_score = Column(Float, nullable=False, default=0.0)

    # Insights stored as JSON strings
    common_strengths = Column(Text, nullable=True)  # JSON string
    common_gaps = Column(Text, nullable=True)  # JSON string

    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    specialization = relationship("Specialization")

