"""
Quiz Generator schemas.
Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


# ============================================================
# ENUMS
# ============================================================

class JobType(str, Enum):
    """Types of generation jobs."""
    FULL = "full"  # Generate all sectors
    SECTOR = "sector"  # Generate a single sector
    CAREER_LEVEL = "career_level"  # Generate for specific career/level
    SOFT_SKILLS = "soft_skills"  # Generate soft skills questions


class JobStatus(str, Enum):
    """Status of a generation job."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ============================================================
# REQUEST SCHEMAS
# ============================================================

class GenerateSectorRequest(BaseModel):
    """Request to generate questions for a specific sector."""
    sector: str = Field(
        ...,
        description="Sector name (e.g., 'technology', 'finance', 'health_social_care', 'education', 'construction')"
    )


class GenerateCareerLevelRequest(BaseModel):
    """Request to generate questions for a specific career and level."""
    sector: str = Field(
        default="technology",
        description="Sector name"
    )
    career: str = Field(
        ...,
        description="Career/role name (e.g., 'FRONTEND_DEVELOPER', 'DATA_SCIENTIST')"
    )
    level: int = Field(
        ...,
        ge=1,
        le=5,
        description="Difficulty level (1-5)"
    )


class GenerateFullRequest(BaseModel):
    """Request to generate all questions (all sectors)."""
    include_soft_skills: bool = Field(
        default=True,
        description="Whether to also generate soft skills questions"
    )


# ============================================================
# RESPONSE SCHEMAS
# ============================================================

class JobResponse(BaseModel):
    """Response for a generation job."""
    job_id: UUID
    job_type: str
    status: str
    parameters: Optional[Dict[str, Any]] = None
    progress_percent: int = 0
    progress_message: Optional[str] = None
    result_summary: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    """Response for list of generation jobs."""
    jobs: List[JobResponse]
    total: int


class CheckpointStatus(BaseModel):
    """Checkpoint status information."""
    has_checkpoint: bool
    completed_chunks: int
    chunks: List[str] = Field(default_factory=list)


class AvailableSectors(BaseModel):
    """Available sectors for generation."""
    sectors: List[str]
    sector_details: Dict[str, Dict[str, List[str]]]


class GenerationStartedResponse(BaseModel):
    """Response when a generation job is started."""
    message: str
    job_id: UUID
    job_type: str
    status: str = "pending"


class SyncGenerationResponse(BaseModel):
    """Response for synchronous (immediate) generation."""
    success: bool
    message: str
    questions_generated: int = 0
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

