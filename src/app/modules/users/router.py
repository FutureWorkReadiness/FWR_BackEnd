"""
User API endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

from src.app.db.session import get_db
from src.app.modules.users.service import UserService
from src.app.modules.benchmarks.service import BenchmarkService

router = APIRouter()


# Request models
class UserRegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class UserLoginRequest(BaseModel):
    email: str
    password: str


class UserUpdateRequest(BaseModel):
    preferred_specialization_id: UUID


# ============================================================
# ENDPOINTS
# ============================================================


@router.post("/register")
def register(data: UserRegisterRequest, db: Session = Depends(get_db)):
    """Register a new user."""
    existing_user = UserService.get_user_by_email(db, data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = UserService.create_user(db=db, email=data.email, password=data.password, name=data.name)

    return {
        "success": True,
        "user": {
            "user_id": str(new_user.user_id),
            "email": new_user.email,
            "name": new_user.name,
            "preferred_specialization_id": (
                str(new_user.preferred_specialization_id) if new_user.preferred_specialization_id else None
            ),
            "readiness_score": new_user.readiness_score,
            "technical_score": new_user.technical_score,
            "soft_skills_score": new_user.soft_skills_score,
            "leadership_score": new_user.leadership_score,
            "created_at": str(new_user.created_at),
        },
    }


@router.post("/login")
def login(data: UserLoginRequest, db: Session = Depends(get_db)):
    """Login a user."""
    user = UserService.get_user_by_email(db, data.email)

    if not user or user.password_hash != data.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "success": True,
        "user": {
            "user_id": str(user.user_id),
            "email": user.email,
            "name": user.name,
            "preferred_specialization_id": (
                str(user.preferred_specialization_id) if user.preferred_specialization_id else None
            ),
            "readiness_score": user.readiness_score,
            "technical_score": user.technical_score,
            "soft_skills_score": user.soft_skills_score,
            "leadership_score": user.leadership_score,
            "created_at": str(user.created_at),
        },
    }


@router.patch("/{user_id}/specialization")
def update_specialization(user_id: UUID, data: UserUpdateRequest, db: Session = Depends(get_db)):
    """Update user's specialization."""
    if data.preferred_specialization_id is None:
        raise HTTPException(status_code=400, detail="Specialization ID is required")

    user = UserService.update_user_specialization(db, user_id, data.preferred_specialization_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "success": True,
        "user": {
            "user_id": str(user.user_id),
            "email": user.email,
            "name": user.name,
            "preferred_specialization_id": (
                str(user.preferred_specialization_id) if user.preferred_specialization_id else None
            ),
        },
    }


@router.get("/{user_id}")
def get_user(user_id: UUID, db: Session = Depends(get_db)):
    """Get user by ID."""
    user = UserService.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user_id": str(user.user_id),
        "email": user.email,
        "name": user.name,
        "preferred_specialization_id": (
            str(user.preferred_specialization_id) if user.preferred_specialization_id else None
        ),
        "readiness_score": user.readiness_score,
        "technical_score": user.technical_score,
        "soft_skills_score": user.soft_skills_score,
        "leadership_score": user.leadership_score,
        "created_at": user.created_at,
    }


@router.get("/{user_id}/peer-benchmark")
def get_peer_benchmark_endpoint(user_id: UUID, db: Session = Depends(get_db)):
    """Get peer benchmarking data comparing user's scores with peers in their specialization."""
    data = BenchmarkService.get_peer_benchmark(db, user_id)

    if not data:
        raise HTTPException(
            status_code=404,
            detail="User not found or no specialization set. Please complete onboarding first.",
        )

    # Check if there's an error (not enough users)
    if "error" in data:
        raise HTTPException(
            status_code=400,
            detail=data.get("message", "Not enough data for peer comparison"),
        )

    return {
        "success": True,
        "data": {
            "specialization_name": data["specialization_name"],
            "total_peers": data["total_peers"],
            "comparisons": data["comparisons"],
            "overall_percentile": data["overall_percentile"],
            "common_strengths": data["common_strengths"],
            "common_gaps": data["common_gaps"],
            "last_updated": data.get("last_updated") or datetime.now().isoformat(),
        },
    }


@router.get("/{user_id}/dashboard")
def get_user_dashboard(user_id: UUID, db: Session = Depends(get_db)):
    """Get dashboard summary for a user."""
    from src.app.modules.quizzes.service import QuizService

    summary = QuizService.get_dashboard_summary(db, user_id)
    if not summary:
        raise HTTPException(status_code=404, detail="User not found")
    return summary

