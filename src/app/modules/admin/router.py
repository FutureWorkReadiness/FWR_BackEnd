"""
Admin API endpoints.
Database management via browser.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from pydantic import BaseModel
from uuid import UUID

from src.app.db.session import get_db
from src.app.modules.sectors.service import SectorService
from src.app.modules.sectors.models import Sector, Branch, Specialization
from src.app.modules.users.service import UserService
from src.app.modules.users.models import User
from src.app.modules.quizzes.service import QuizService
from src.app.modules.quizzes.models import Quiz

router = APIRouter()


# ============================================================
# REQUEST/RESPONSE MODELS
# ============================================================


class SectorCreate(BaseModel):
    name: str
    description: Optional[str] = None


class SectorUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class BranchCreate(BaseModel):
    name: str
    description: Optional[str] = None
    sector_id: UUID


class BranchUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sector_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class SpecializationCreate(BaseModel):
    name: str
    description: Optional[str] = None
    branch_id: UUID


class SpecializationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    branch_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    readiness_score: Optional[float] = None
    technical_score: Optional[float] = None
    soft_skills_score: Optional[float] = None
    preferred_specialization_id: Optional[UUID] = None


# ============================================================
# STATISTICS
# ============================================================


@router.get("/stats")
def get_statistics(db: Session = Depends(get_db)):
    """Get database statistics."""
    return {
        "sectors": db.query(Sector).count(),
        "active_sectors": db.query(Sector).filter(Sector.is_active == True).count(),
        "branches": db.query(Branch).count(),
        "active_branches": db.query(Branch).filter(Branch.is_active == True).count(),
        "specializations": db.query(Specialization).count(),
        "active_specializations": db.query(Specialization).filter(Specialization.is_active == True).count(),
        "quizzes": db.query(Quiz).count(),
        "users": db.query(User).count(),
        "active_users": db.query(User).filter(User.is_active == True).count(),
        "quiz_attempts": QuizService.get_quiz_attempt_count(db),
        "avg_readiness_score": db.query(func.avg(User.readiness_score)).scalar() or 0.0,
    }


# ============================================================
# SECTORS
# ============================================================


@router.get("/sectors")
def get_all_sectors(db: Session = Depends(get_db)):
    """Get all sectors with branch counts."""
    sectors = SectorService.get_all_sectors(db, active_only=False)
    result = []
    for sector in sectors:
        branch_count = SectorService.get_sector_branch_count(db, sector.sector_id)
        result.append({
            "sector_id": str(sector.sector_id),
            "name": sector.name,
            "description": sector.description,
            "is_active": sector.is_active,
            "branch_count": branch_count,
            "created_at": sector.created_at.isoformat() if sector.created_at else None,
        })
    return result


@router.post("/sectors")
def create_sector(sector: SectorCreate, db: Session = Depends(get_db)):
    """Create a new sector."""
    existing = db.query(Sector).filter(Sector.name == sector.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Sector already exists")

    new_sector = SectorService.create_sector(db, sector.name, sector.description)
    return {"success": True, "sector_id": str(new_sector.sector_id), "message": "Sector created"}


@router.put("/sectors/{sector_id}")
def update_sector(sector_id: UUID, sector: SectorUpdate, db: Session = Depends(get_db)):
    """Update a sector."""
    updated = SectorService.update_sector(
        db,
        sector_id,
        name=sector.name,
        description=sector.description,
        is_active=sector.is_active,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Sector not found")
    return {"success": True, "message": "Sector updated"}


@router.delete("/sectors/{sector_id}")
def delete_sector(sector_id: UUID, db: Session = Depends(get_db)):
    """Delete a sector (soft delete by setting is_active=False)."""
    success = SectorService.delete_sector(db, sector_id, soft_delete=True)
    if not success:
        raise HTTPException(status_code=404, detail="Sector not found")
    return {"success": True, "message": "Sector deactivated"}


# ============================================================
# BRANCHES
# ============================================================


@router.get("/branches")
def get_all_branches(sector_id: Optional[UUID] = None, db: Session = Depends(get_db)):
    """Get all branches, optionally filtered by sector."""
    branches = SectorService.get_all_branches(db, sector_id=sector_id, active_only=False)

    result = []
    for branch in branches:
        sector = SectorService.get_sector_by_id(db, branch.sector_id, active_only=False)
        spec_count = SectorService.get_branch_specialization_count(db, branch.branch_id)
        result.append({
            "branch_id": str(branch.branch_id),
            "name": branch.name,
            "description": branch.description,
            "sector_id": str(branch.sector_id),
            "sector_name": sector.name if sector else None,
            "is_active": branch.is_active,
            "specialization_count": spec_count,
        })
    return result


@router.post("/branches")
def create_branch(branch: BranchCreate, db: Session = Depends(get_db)):
    """Create a new branch."""
    sector = SectorService.get_sector_by_id(db, branch.sector_id, active_only=False)
    if not sector:
        raise HTTPException(status_code=404, detail="Sector not found")

    new_branch = SectorService.create_branch(db, branch.name, branch.sector_id, branch.description)
    return {"success": True, "branch_id": str(new_branch.branch_id), "message": "Branch created"}


@router.put("/branches/{branch_id}")
def update_branch(branch_id: UUID, branch: BranchUpdate, db: Session = Depends(get_db)):
    """Update a branch."""
    updated = SectorService.update_branch(
        db,
        branch_id,
        name=branch.name,
        description=branch.description,
        sector_id=branch.sector_id,
        is_active=branch.is_active,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Branch not found")
    return {"success": True, "message": "Branch updated"}


@router.delete("/branches/{branch_id}")
def delete_branch(branch_id: UUID, db: Session = Depends(get_db)):
    """Delete a branch."""
    success = SectorService.delete_branch(db, branch_id, soft_delete=True)
    if not success:
        raise HTTPException(status_code=404, detail="Branch not found")
    return {"success": True, "message": "Branch deactivated"}


# ============================================================
# SPECIALIZATIONS
# ============================================================


@router.get("/specializations")
def get_all_specializations(branch_id: Optional[UUID] = None, db: Session = Depends(get_db)):
    """Get all specializations, optionally filtered by branch."""
    specializations = SectorService.get_all_specializations(db, branch_id=branch_id, active_only=False)

    result = []
    for spec in specializations:
        branch = SectorService.get_branch_by_id(db, spec.branch_id, active_only=False)
        sector = SectorService.get_sector_by_id(db, branch.sector_id, active_only=False) if branch else None
        quiz_count = QuizService.get_quiz_count_by_specialization(db, spec.specialization_id)
        result.append({
            "specialization_id": str(spec.specialization_id),
            "name": spec.name,
            "description": spec.description,
            "branch_id": str(spec.branch_id),
            "branch_name": branch.name if branch else None,
            "sector_name": sector.name if sector else None,
            "is_active": spec.is_active,
            "quiz_count": quiz_count,
        })
    return result


@router.post("/specializations")
def create_specialization(spec: SpecializationCreate, db: Session = Depends(get_db)):
    """Create a new specialization."""
    branch = SectorService.get_branch_by_id(db, spec.branch_id, active_only=False)
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    new_spec = SectorService.create_specialization(db, spec.name, spec.branch_id, spec.description)
    return {"success": True, "specialization_id": str(new_spec.specialization_id), "message": "Specialization created"}


@router.put("/specializations/{spec_id}")
def update_specialization(spec_id: UUID, spec: SpecializationUpdate, db: Session = Depends(get_db)):
    """Update a specialization."""
    updated = SectorService.update_specialization(
        db,
        spec_id,
        name=spec.name,
        description=spec.description,
        branch_id=spec.branch_id,
        is_active=spec.is_active,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Specialization not found")
    return {"success": True, "message": "Specialization updated"}


@router.delete("/specializations/{spec_id}")
def delete_specialization(spec_id: UUID, db: Session = Depends(get_db)):
    """Delete a specialization."""
    success = SectorService.delete_specialization(db, spec_id, soft_delete=True)
    if not success:
        raise HTTPException(status_code=404, detail="Specialization not found")
    return {"success": True, "message": "Specialization deactivated"}


# ============================================================
# USERS
# ============================================================


@router.get("/users")
def get_all_users(db: Session = Depends(get_db)):
    """Get all users."""
    users = UserService.get_all_users(db)
    result = []
    for user in users:
        spec = None
        if user.preferred_specialization_id:
            spec = SectorService.get_specialization_by_id(db, user.preferred_specialization_id, active_only=False)

        result.append({
            "user_id": str(user.user_id),
            "name": user.name,
            "email": user.email,
            "is_active": user.is_active,
            "readiness_score": user.readiness_score,
            "technical_score": user.technical_score,
            "soft_skills_score": user.soft_skills_score,
            "preferred_specialization_id": (
                str(user.preferred_specialization_id) if user.preferred_specialization_id else None
            ),
            "specialization_name": spec.name if spec else None,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        })
    return result


@router.put("/users/{user_id}")
def update_user(user_id: UUID, user: UserUpdate, db: Session = Depends(get_db)):
    """Update a user."""
    updated = UserService.update_user(
        db,
        user_id,
        name=user.name,
        email=user.email,
        readiness_score=user.readiness_score,
        technical_score=user.technical_score,
        soft_skills_score=user.soft_skills_score,
        preferred_specialization_id=user.preferred_specialization_id,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return {"success": True, "message": "User updated"}

