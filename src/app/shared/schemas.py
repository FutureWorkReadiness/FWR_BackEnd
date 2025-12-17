"""
Common/shared schemas.
Pydantic models used across multiple modules.
"""

from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID


class ReadinessSnapshot(BaseModel):
    """Snapshot of user's readiness scores."""

    overall: float
    technical: float
    soft: float


class FeedbackDetail(BaseModel):
    """Detailed feedback for quiz performance."""

    overall: str
    strengths: str
    weaknesses: str
    recommendations: List[str]


class ScoreImpact(BaseModel):
    """Impact of quiz on user scores."""

    category: str
    old_score: float
    new_score: float
    increase: float


class RecentAttempt(BaseModel):
    """Summary of a recent quiz attempt."""

    attempt_id: UUID
    quiz_id: UUID
    score: float
    passed: bool
    completed_at: Optional[str] = None


class DashboardResponse(BaseModel):
    """Response schema for user dashboard."""

    readiness: ReadinessSnapshot
    recent_attempts: List[RecentAttempt]

