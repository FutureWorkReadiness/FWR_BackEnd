"""
Quiz Generator API endpoints.

Provides endpoints to:
- Trigger quiz generation (sync or async)
- Check generation job status
- Get checkpoint information
- List available sectors and careers
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from src.app.db.session import get_db
from src.app.modules.quiz_generator.service import QuizGeneratorService
from src.app.modules.quiz_generator.schema import (
    JobType,
    JobStatus,
    GenerateSectorRequest,
    GenerateCareerLevelRequest,
    GenerateFullRequest,
    JobResponse,
    JobListResponse,
    CheckpointStatus,
    AvailableSectors,
    GenerationStartedResponse,
    SyncGenerationResponse,
)

router = APIRouter()


# ============================================================
# INFO ENDPOINTS (Read-only)
# ============================================================


@router.get("/sectors", response_model=AvailableSectors)
def get_available_sectors():
    """
    Get list of available sectors and their careers.

    Returns all sectors that can be used for quiz generation,
    along with the careers/branches within each sector.
    """
    return QuizGeneratorService.get_available_sectors()


@router.get("/checkpoint", response_model=CheckpointStatus)
def get_checkpoint_status():
    """
    Get the current checkpoint status.

    Shows how many chunks have been completed in previous runs.
    Useful for resuming interrupted generation.
    """
    return QuizGeneratorService.get_checkpoint_status()


@router.get("/api-status")
def check_api_status():
    """
    Check if the Gemini API key is configured.

    Returns whether the GEMINI_API_KEY environment variable is set.
    """
    is_configured = QuizGeneratorService.check_api_key()
    return {
        "api_key_configured": is_configured,
        "message": (
            "Ready for generation" if is_configured else "GEMINI_API_KEY not set"
        ),
    }


# ============================================================
# JOB MANAGEMENT ENDPOINTS
# ============================================================


@router.get("/jobs", response_model=JobListResponse)
def list_jobs(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    List all generation jobs.

    Optionally filter by status: pending, running, completed, failed, cancelled
    """
    jobs = QuizGeneratorService.get_all_jobs(db, status, limit, offset)
    return {"jobs": jobs, "total": len(jobs)}


@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: UUID, db: Session = Depends(get_db)):
    """
    Get a specific job by ID.

    Use this to check the status and progress of a running job.
    """
    job = QuizGeneratorService.get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.delete("/jobs/{job_id}", status_code=204)
def delete_job(job_id: UUID, db: Session = Depends(get_db)):
    """
    Delete a job record.

    Note: This only deletes the job record, not any generated content.
    """
    deleted = QuizGeneratorService.delete_job(db, job_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Job not found")
    return None


# ============================================================
# SYNCHRONOUS GENERATION ENDPOINTS (Immediate execution)
# ============================================================


@router.post("/generate/career-level", response_model=SyncGenerationResponse)
def generate_career_level(
    request: GenerateCareerLevelRequest,
):
    """
    Generate questions for a specific career and level (SYNCHRONOUS).

    ⚠️ This runs immediately and blocks until complete (can take 5-15 minutes).
    Best for testing or generating a single career/level.

    Example:
    - sector: "technology"
    - career: "FRONTEND_DEVELOPER"
    - level: 1
    """
    result = QuizGeneratorService.generate_career_level_sync(
        sector=request.sector, career=request.career, level=request.level
    )
    return result


@router.post("/generate/soft-skills", response_model=SyncGenerationResponse)
def generate_soft_skills():
    """
    Generate soft skills questions (SYNCHRONOUS).

    ⚠️ This runs immediately and blocks until complete (can take 5-10 minutes).
    """
    result = QuizGeneratorService.generate_soft_skills_sync()
    return result


@router.post("/generate/sector", response_model=SyncGenerationResponse)
def generate_sector(
    request: GenerateSectorRequest,
):
    """
    Generate questions for an entire sector (SYNCHRONOUS).

    ⚠️ WARNING: This can take HOURS to complete as it generates
    questions for all careers (5 levels each) in the sector.

    Consider using the async endpoint (/generate/sector/async) instead
    for long-running generation.

    Valid sectors: technology, finance, health_social_care, education, construction
    """
    result = QuizGeneratorService.generate_sector_sync(sector=request.sector)
    return result


# ============================================================
# ASYNCHRONOUS GENERATION ENDPOINTS (Background tasks)
# ============================================================


@router.post(
    "/generate/career-level/async",
    response_model=GenerationStartedResponse,
    status_code=202,
)
def generate_career_level_async(
    request: GenerateCareerLevelRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Generate questions for a specific career and level (ASYNC).

    Returns immediately with a job_id. Use GET /jobs/{job_id} to check progress.
    """
    if not QuizGeneratorService.check_api_key():
        raise HTTPException(status_code=503, detail="GEMINI_API_KEY not configured")

    # Create job record
    job = QuizGeneratorService.create_job(
        db,
        job_type=JobType.CAREER_LEVEL,
        parameters={
            "sector": request.sector,
            "career": request.career,
            "level": request.level,
        },
    )

    # Schedule background task
    background_tasks.add_task(
        QuizGeneratorService.run_generation_job,
        db,
        job.job_id,
        JobType.CAREER_LEVEL,
        {"sector": request.sector, "career": request.career, "level": request.level},
    )

    return {
        "message": f"Generation started for {request.sector}/{request.career} Level {request.level}",
        "job_id": job.job_id,
        "job_type": job.job_type,
        "status": job.status,
    }


@router.post(
    "/generate/soft-skills/async",
    response_model=GenerationStartedResponse,
    status_code=202,
)
def generate_soft_skills_async(
    background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    """
    Generate soft skills questions (ASYNC).

    Returns immediately with a job_id. Use GET /jobs/{job_id} to check progress.
    """
    if not QuizGeneratorService.check_api_key():
        raise HTTPException(status_code=503, detail="GEMINI_API_KEY not configured")

    # Create job record
    job = QuizGeneratorService.create_job(
        db, job_type=JobType.SOFT_SKILLS, parameters={"type": "soft_skills"}
    )

    # Schedule background task
    background_tasks.add_task(
        QuizGeneratorService.run_generation_job,
        db,
        job.job_id,
        JobType.SOFT_SKILLS,
        {"type": "soft_skills"},
    )

    return {
        "message": "Soft skills generation started",
        "job_id": job.job_id,
        "job_type": job.job_type,
        "status": job.status,
    }


@router.post(
    "/generate/sector/async", response_model=GenerationStartedResponse, status_code=202
)
def generate_sector_async(
    request: GenerateSectorRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Generate questions for an entire sector (ASYNC).

    Returns immediately with a job_id. Use GET /jobs/{job_id} to check progress.

    ⚠️ This can take hours to complete as it generates questions
    for all careers (5 levels each) in the sector.
    """
    if not QuizGeneratorService.check_api_key():
        raise HTTPException(status_code=503, detail="GEMINI_API_KEY not configured")

    # Validate sector
    sectors_info = QuizGeneratorService.get_available_sectors()
    if request.sector not in sectors_info["sectors"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown sector: {request.sector}. Valid sectors: {sectors_info['sectors']}",
        )

    # Create job record
    job = QuizGeneratorService.create_job(
        db, job_type=JobType.SECTOR, parameters={"sector": request.sector}
    )

    # Schedule background task
    background_tasks.add_task(
        QuizGeneratorService.run_generation_job,
        db,
        job.job_id,
        JobType.SECTOR,
        {"sector": request.sector},
    )

    return {
        "message": f"Sector generation started for '{request.sector}'",
        "job_id": job.job_id,
        "job_type": job.job_type,
        "status": job.status,
    }


@router.post(
    "/generate/full/async", response_model=GenerationStartedResponse, status_code=202
)
def generate_full_async(
    request: GenerateFullRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Generate ALL questions for ALL sectors (ASYNC).

    ⚠️ WARNING: This is a very long-running operation that can take MANY HOURS.

    Returns immediately with a job_id. Use GET /jobs/{job_id} to check progress.
    """
    if not QuizGeneratorService.check_api_key():
        raise HTTPException(status_code=503, detail="GEMINI_API_KEY not configured")

    # Create job record
    job = QuizGeneratorService.create_job(
        db,
        job_type=JobType.FULL,
        parameters={"include_soft_skills": request.include_soft_skills},
    )

    # Schedule background task
    background_tasks.add_task(
        QuizGeneratorService.run_generation_job,
        db,
        job.job_id,
        JobType.FULL,
        {"include_soft_skills": request.include_soft_skills},
    )

    return {
        "message": "Full generation started (all sectors)",
        "job_id": job.job_id,
        "job_type": job.job_type,
        "status": job.status,
    }
