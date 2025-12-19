"""
Quiz Generator service.
Business logic for quiz generation operations.

Wraps the gemini_pkg generator and provides both sync and async generation.
"""

import os
import logging
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

from src.app.modules.quiz_generator.models import GenerationJob
from src.app.modules.quiz_generator.schema import (
    JobType,
    JobStatus,
    GenerateSectorRequest,
    GenerateCareerLevelRequest,
)

# Import from the local gemini_pkg package
from gemini_pkg.config.settings import (
    SECTOR_TRACKS,
    get_all_careers_for_sector,
    load_checkpoint,
)
from gemini_pkg.services.generator import GeminiQuizGeneratorV4

logger = logging.getLogger(__name__)


class QuizGeneratorService:
    """Service class for quiz generation operations."""

    # ============================================================
    # JOB MANAGEMENT
    # ============================================================

    @staticmethod
    def create_job(
        db: Session,
        job_type: JobType,
        parameters: Optional[Dict[str, Any]] = None
    ) -> GenerationJob:
        """Create a new generation job record."""
        job = GenerationJob(
            job_type=job_type.value,
            status=JobStatus.PENDING.value,
            parameters=parameters,
            progress_percent=0,
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        logger.info(f"Created generation job: {job.job_id} ({job_type.value})")
        return job

    @staticmethod
    def get_job_by_id(db: Session, job_id: UUID) -> Optional[GenerationJob]:
        """Get a job by ID."""
        return db.query(GenerationJob).filter(
            GenerationJob.job_id == job_id
        ).first()

    @staticmethod
    def get_all_jobs(
        db: Session,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[GenerationJob]:
        """Get all jobs, optionally filtered by status."""
        query = db.query(GenerationJob)
        if status:
            query = query.filter(GenerationJob.status == status)
        return query.order_by(
            GenerationJob.created_at.desc()
        ).offset(offset).limit(limit).all()

    @staticmethod
    def update_job_status(
        db: Session,
        job_id: UUID,
        status: JobStatus,
        progress_percent: Optional[int] = None,
        progress_message: Optional[str] = None,
        result_summary: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> Optional[GenerationJob]:
        """Update job status and progress."""
        job = db.query(GenerationJob).filter(
            GenerationJob.job_id == job_id
        ).first()

        if not job:
            return None

        job.status = status.value

        if progress_percent is not None:
            job.progress_percent = progress_percent
        if progress_message is not None:
            job.progress_message = progress_message
        if result_summary is not None:
            job.result_summary = result_summary
        if error_message is not None:
            job.error_message = error_message

        # Update timestamps
        if status == JobStatus.RUNNING and job.started_at is None:
            job.started_at = datetime.utcnow()
        if status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
            job.completed_at = datetime.utcnow()

        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def delete_job(db: Session, job_id: UUID) -> bool:
        """Delete a job. Returns True if deleted."""
        job = db.query(GenerationJob).filter(
            GenerationJob.job_id == job_id
        ).first()

        if job:
            db.delete(job)
            db.commit()
            return True
        return False

    # ============================================================
    # CHECKPOINT & SECTORS INFO
    # ============================================================

    @staticmethod
    def get_checkpoint_status() -> Dict[str, Any]:
        """Get the current checkpoint status."""
        checkpoint = load_checkpoint()
        if not checkpoint:
            return {
                "has_checkpoint": False,
                "completed_chunks": 0,
                "chunks": []
            }

        completed = [k for k, v in checkpoint.items() if v == "done"]
        return {
            "has_checkpoint": True,
            "completed_chunks": len(completed),
            "chunks": sorted(completed)[:100]  # Limit to first 100
        }

    @staticmethod
    def get_available_sectors() -> Dict[str, Any]:
        """Get list of available sectors and their careers."""
        sectors = list(SECTOR_TRACKS.keys())
        sector_details = {}

        for sector in sectors:
            sector_details[sector] = SECTOR_TRACKS[sector]

        return {
            "sectors": sectors,
            "sector_details": sector_details
        }

    # ============================================================
    # SYNCHRONOUS GENERATION (runs immediately)
    # ============================================================

    @staticmethod
    def check_api_key() -> bool:
        """Check if GEMINI_API_KEY is configured."""
        api_key = os.getenv("GEMINI_API_KEY")
        return bool(api_key)

    @staticmethod
    def generate_career_level_sync(
        sector: str,
        career: str,
        level: int
    ) -> Dict[str, Any]:
        """
        Generate questions for a specific career/level synchronously.
        This runs immediately and blocks until complete.
        
        Best for testing or generating a single career/level.
        """
        if not QuizGeneratorService.check_api_key():
            return {
                "success": False,
                "message": "GEMINI_API_KEY not configured",
                "questions_generated": 0,
                "error": "Missing API key"
            }

        try:
            logger.info(f"Starting sync generation: {sector}/{career} Level {level}")
            generator = GeminiQuizGeneratorV4()
            generator.generate_for_career_level(sector, career, level)

            # Check results
            results = generator.results_bank
            questions_count = 0

            if sector in results and career in results[sector]:
                level_key = f"level_{level}"
                if level_key in results[sector][career]:
                    quiz_pool = results[sector][career][level_key].get("quiz_pool", [])
                    questions_count = len(quiz_pool)

            return {
                "success": True,
                "message": f"Generated {questions_count} questions for {sector}/{career} Level {level}",
                "questions_generated": questions_count,
                "details": {
                    "sector": sector,
                    "career": career,
                    "level": level
                }
            }

        except EnvironmentError as e:
            logger.error(f"Environment error: {e}")
            return {
                "success": False,
                "message": "Environment configuration error",
                "questions_generated": 0,
                "error": str(e)
            }
        except Exception as e:
            logger.exception(f"Generation error: {e}")
            return {
                "success": False,
                "message": "Generation failed",
                "questions_generated": 0,
                "error": str(e)
            }

    @staticmethod
    def generate_soft_skills_sync() -> Dict[str, Any]:
        """
        Generate soft skills questions synchronously.
        """
        if not QuizGeneratorService.check_api_key():
            return {
                "success": False,
                "message": "GEMINI_API_KEY not configured",
                "questions_generated": 0,
                "error": "Missing API key"
            }

        try:
            logger.info("Starting sync soft skills generation")
            generator = GeminiQuizGeneratorV4()
            generator.generate_soft_skills_block()

            # Check results
            results = generator.results_bank
            questions_count = 0

            if "soft_skills" in results:
                quiz_pool = results["soft_skills"].get("quiz_pool", [])
                questions_count = len(quiz_pool)

            return {
                "success": True,
                "message": f"Generated {questions_count} soft skills questions",
                "questions_generated": questions_count,
                "details": {"type": "soft_skills"}
            }

        except Exception as e:
            logger.exception(f"Soft skills generation error: {e}")
            return {
                "success": False,
                "message": "Generation failed",
                "questions_generated": 0,
                "error": str(e)
            }

    @staticmethod
    def generate_sector_sync(sector: str) -> Dict[str, Any]:
        """
        Generate questions for an entire sector synchronously.
        WARNING: This can take a VERY long time (hours).
        """
        if not QuizGeneratorService.check_api_key():
            return {
                "success": False,
                "message": "GEMINI_API_KEY not configured",
                "questions_generated": 0,
                "error": "Missing API key"
            }

        if sector not in SECTOR_TRACKS:
            return {
                "success": False,
                "message": f"Unknown sector: {sector}",
                "questions_generated": 0,
                "error": f"Valid sectors: {list(SECTOR_TRACKS.keys())}"
            }

        try:
            logger.info(f"Starting sync sector generation: {sector}")
            generator = GeminiQuizGeneratorV4()
            generator.generate_sector(sector)

            # Count results
            results = generator.results_bank
            total_questions = 0

            if sector in results:
                for career_data in results[sector].values():
                    for level_data in career_data.values():
                        if isinstance(level_data, dict) and "quiz_pool" in level_data:
                            total_questions += len(level_data["quiz_pool"])

            careers = get_all_careers_for_sector(sector)

            return {
                "success": True,
                "message": f"Generated {total_questions} questions for sector '{sector}'",
                "questions_generated": total_questions,
                "details": {
                    "sector": sector,
                    "careers_processed": len(careers),
                    "levels_per_career": 5
                }
            }

        except Exception as e:
            logger.exception(f"Sector generation error: {e}")
            return {
                "success": False,
                "message": "Generation failed",
                "questions_generated": 0,
                "error": str(e)
            }

    # ============================================================
    # ASYNC GENERATION (with job tracking)
    # ============================================================

    @staticmethod
    def run_generation_job(
        db: Session,
        job_id: UUID,
        job_type: JobType,
        parameters: Optional[Dict[str, Any]] = None
    ):
        """
        Run a generation job. This should be called from a background task.
        
        Updates the job status in the database as it progresses.
        """
        # Update to running
        QuizGeneratorService.update_job_status(
            db, job_id,
            status=JobStatus.RUNNING,
            progress_percent=0,
            progress_message="Initializing generator..."
        )

        try:
            generator = GeminiQuizGeneratorV4()
            total_questions = 0

            if job_type == JobType.CAREER_LEVEL:
                sector = parameters.get("sector", "technology")
                career = parameters["career"]
                level = parameters["level"]

                QuizGeneratorService.update_job_status(
                    db, job_id,
                    status=JobStatus.RUNNING,
                    progress_percent=10,
                    progress_message=f"Generating {sector}/{career} Level {level}..."
                )

                generator.generate_for_career_level(sector, career, level)

                # Count results
                if sector in generator.results_bank:
                    career_data = generator.results_bank[sector].get(career, {})
                    level_data = career_data.get(f"level_{level}", {})
                    total_questions = len(level_data.get("quiz_pool", []))

            elif job_type == JobType.SOFT_SKILLS:
                QuizGeneratorService.update_job_status(
                    db, job_id,
                    status=JobStatus.RUNNING,
                    progress_percent=10,
                    progress_message="Generating soft skills questions..."
                )

                generator.generate_soft_skills_block()

                if "soft_skills" in generator.results_bank:
                    total_questions = len(
                        generator.results_bank["soft_skills"].get("quiz_pool", [])
                    )

            elif job_type == JobType.SECTOR:
                sector = parameters["sector"]
                careers = get_all_careers_for_sector(sector)

                QuizGeneratorService.update_job_status(
                    db, job_id,
                    status=JobStatus.RUNNING,
                    progress_percent=5,
                    progress_message=f"Generating sector '{sector}' ({len(careers)} careers)..."
                )

                generator.generate_sector(sector)

                # Count results
                if sector in generator.results_bank:
                    for career_data in generator.results_bank[sector].values():
                        for level_data in career_data.values():
                            if isinstance(level_data, dict) and "quiz_pool" in level_data:
                                total_questions += len(level_data["quiz_pool"])

            elif job_type == JobType.FULL:
                include_soft_skills = parameters.get("include_soft_skills", True)

                QuizGeneratorService.update_job_status(
                    db, job_id,
                    status=JobStatus.RUNNING,
                    progress_percent=5,
                    progress_message="Generating all sectors..."
                )

                generator.generate_all()

                # Count all results
                for sector_data in generator.results_bank.values():
                    if isinstance(sector_data, dict):
                        if "quiz_pool" in sector_data:
                            # This is soft_skills
                            total_questions += len(sector_data["quiz_pool"])
                        else:
                            # This is a sector
                            for career_data in sector_data.values():
                                if isinstance(career_data, dict):
                                    for level_data in career_data.values():
                                        if isinstance(level_data, dict) and "quiz_pool" in level_data:
                                            total_questions += len(level_data["quiz_pool"])

            # Mark as completed
            QuizGeneratorService.update_job_status(
                db, job_id,
                status=JobStatus.COMPLETED,
                progress_percent=100,
                progress_message="Generation complete!",
                result_summary={
                    "questions_generated": total_questions,
                    "job_type": job_type.value,
                    "parameters": parameters
                }
            )

            logger.info(f"Job {job_id} completed: {total_questions} questions generated")

        except Exception as e:
            logger.exception(f"Job {job_id} failed: {e}")
            QuizGeneratorService.update_job_status(
                db, job_id,
                status=JobStatus.FAILED,
                progress_percent=0,
                progress_message="Generation failed",
                error_message=str(e)
            )

