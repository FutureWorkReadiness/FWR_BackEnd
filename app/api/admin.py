"""
Admin API endpoints for database management via browser
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..models import models_hierarchical as models
from ..database import get_db

router = APIRouter()

# Request/Response Models
class SectorCreate(schemas.SectorCreate):
    pass

class SectorUpdate(schemas.SectorUpdate):
    pass

class BranchCreate(schemas.BranchCreate):
    pass

class BranchUpdate(schemas.BranchUpdate):
    pass

class SpecializationCreate(schemas.SpecializationCreate):
    pass

class SpecializationUpdate(schemas.SpecializationUpdate):
    pass

class UserUpdate(schemas.UserUpdate):
    pass

# ============================================================
# SECTORS
# ============================================================

@router.get("/admin/sectors")
def get_all_sectors(db: Session = Depends(get_db)):
    """Get all sectors with branch counts"""
    sectors = db.query(models.Sector).all()
    result = []
    for sector in sectors:
        branch_count = db.query(models.Branch).filter(models.Branch.sector_id == sector.id).count()
        result.append({
            "id": sector.id,
            "name": sector.name,
            "description": sector.description,
            "is_active": sector.is_active,
            "branch_count": branch_count,
            "created_at": sector.created_at.isoformat() if sector.created_at else None
        })
    return result

@router.post("/admin/sectors")
def create_sector(sector: SectorCreate, db: Session = Depends(get_db)):
    """Create a new sector"""
    existing = db.query(models.Sector).filter(models.Sector.name == sector.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Sector already exists")
    
    new_sector = models.Sector(name=sector.name, description=sector.description)
    db.add(new_sector)
    db.commit()
    db.refresh(new_sector)
    return {"success": True, "id": new_sector.id, "message": "Sector created"}

@router.put("/admin/sectors/{sector_id}")
def update_sector(sector_id: int, sector: SectorUpdate, db: Session = Depends(get_db)):
    """Update a sector"""
    db_sector = db.query(models.Sector).filter(models.Sector.id == sector_id).first()
    if not db_sector:
        raise HTTPException(status_code=404, detail="Sector not found")
    
    if sector.name is not None:
        db_sector.name = sector.name
    if sector.description is not None:
        db_sector.description = sector.description
    if sector.is_active is not None:
        db_sector.is_active = sector.is_active
    
    db.commit()
    db.refresh(db_sector)
    return {"success": True, "message": "Sector updated"}

@router.delete("/admin/sectors/{sector_id}")
def delete_sector(sector_id: int, db: Session = Depends(get_db)):
    """Delete a sector (soft delete by setting is_active=False)"""
    sector = db.query(models.Sector).filter(models.Sector.id == sector_id).first()
    if not sector:
        raise HTTPException(status_code=404, detail="Sector not found")
    
    sector.is_active = False
    db.commit()
    return {"success": True, "message": "Sector deactivated"}

# ============================================================
# BRANCHES
# ============================================================

@router.get("/admin/branches")
def get_all_branches(sector_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get all branches, optionally filtered by sector"""
    query = db.query(models.Branch)
    if sector_id:
        query = query.filter(models.Branch.sector_id == sector_id)
    
    branches = query.all()
    result = []
    for branch in branches:
        sector = db.query(models.Sector).filter(models.Sector.id == branch.sector_id).first()
        spec_count = db.query(models.Specialization).filter(models.Specialization.branch_id == branch.id).count()
        result.append({
            "id": branch.id,
            "name": branch.name,
            "description": branch.description,
            "sector_id": branch.sector_id,
            "sector_name": sector.name if sector else None,
            "is_active": branch.is_active,
            "specialization_count": spec_count
        })
    return result

@router.post("/admin/branches")
def create_branch(branch: BranchCreate, db: Session = Depends(get_db)):
    """Create a new branch"""
    # Verify sector exists
    sector = db.query(models.Sector).filter(models.Sector.id == branch.sector_id).first()
    if not sector:
        raise HTTPException(status_code=404, detail="Sector not found")
    
    new_branch = models.Branch(
        name=branch.name,
        description=branch.description,
        sector_id=branch.sector_id
    )
    db.add(new_branch)
    db.commit()
    db.refresh(new_branch)
    return {"success": True, "id": new_branch.id, "message": "Branch created"}

@router.put("/admin/branches/{branch_id}")
def update_branch(branch_id: int, branch: BranchUpdate, db: Session = Depends(get_db)):
    """Update a branch"""
    db_branch = db.query(models.Branch).filter(models.Branch.id == branch_id).first()
    if not db_branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    if branch.name is not None:
        db_branch.name = branch.name
    if branch.description is not None:
        db_branch.description = branch.description
    if branch.sector_id is not None:
        db_branch.sector_id = branch.sector_id
    if branch.is_active is not None:
        db_branch.is_active = branch.is_active
    
    db.commit()
    return {"success": True, "message": "Branch updated"}

@router.delete("/admin/branches/{branch_id}")
def delete_branch(branch_id: int, db: Session = Depends(get_db)):
    """Delete a branch"""
    branch = db.query(models.Branch).filter(models.Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    branch.is_active = False
    db.commit()
    return {"success": True, "message": "Branch deactivated"}

# ============================================================
# SPECIALIZATIONS
# ============================================================

@router.get("/admin/specializations")
def get_all_specializations(branch_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get all specializations, optionally filtered by branch"""
    query = db.query(models.Specialization)
    if branch_id:
        query = query.filter(models.Specialization.branch_id == branch_id)
    
    specializations = query.all()
    result = []
    for spec in specializations:
        branch = db.query(models.Branch).filter(models.Branch.id == spec.branch_id).first()
        sector = db.query(models.Sector).filter(models.Sector.id == branch.sector_id).first() if branch else None
        quiz_count = db.query(models.Quiz).filter(models.Quiz.specialization_id == spec.id).count()
        result.append({
            "id": spec.id,
            "name": spec.name,
            "description": spec.description,
            "branch_id": spec.branch_id,
            "branch_name": branch.name if branch else None,
            "sector_name": sector.name if sector else None,
            "is_active": spec.is_active,
            "quiz_count": quiz_count
        })
    return result

@router.post("/admin/specializations")
def create_specialization(spec: SpecializationCreate, db: Session = Depends(get_db)):
    """Create a new specialization"""
    branch = db.query(models.Branch).filter(models.Branch.id == spec.branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    new_spec = models.Specialization(
        name=spec.name,
        description=spec.description,
        branch_id=spec.branch_id
    )
    db.add(new_spec)
    db.commit()
    db.refresh(new_spec)
    return {"success": True, "id": new_spec.id, "message": "Specialization created"}

@router.put("/admin/specializations/{spec_id}")
def update_specialization(spec_id: int, spec: SpecializationUpdate, db: Session = Depends(get_db)):
    """Update a specialization"""
    db_spec = db.query(models.Specialization).filter(models.Specialization.id == spec_id).first()
    if not db_spec:
        raise HTTPException(status_code=404, detail="Specialization not found")
    
    if spec.name is not None:
        db_spec.name = spec.name
    if spec.description is not None:
        db_spec.description = spec.description
    if spec.branch_id is not None:
        db_spec.branch_id = spec.branch_id
    if spec.is_active is not None:
        db_spec.is_active = spec.is_active
    
    db.commit()
    return {"success": True, "message": "Specialization updated"}

@router.delete("/admin/specializations/{spec_id}")
def delete_specialization(spec_id: int, db: Session = Depends(get_db)):
    """Delete a specialization"""
    spec = db.query(models.Specialization).filter(models.Specialization.id == spec_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail="Specialization not found")
    
    spec.is_active = False
    db.commit()
    return {"success": True, "message": "Specialization deactivated"}

# ============================================================
# USERS
# ============================================================

@router.get("/admin/users")
def get_all_users(db: Session = Depends(get_db)):
    """Get all users"""
    users = db.query(models.User).all()
    result = []
    for user in users:
        spec = None
        if user.preferred_specialization_id:
            spec = db.query(models.Specialization).filter(
                models.Specialization.id == user.preferred_specialization_id
            ).first()
        
        result.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "is_active": user.is_active,
            "readiness_score": user.readiness_score,
            "technical_score": user.technical_score,
            "soft_skills_score": user.soft_skills_score,
            "preferred_specialization_id": user.preferred_specialization_id,
            "specialization_name": spec.name if spec else None,
            "created_at": user.created_at.isoformat() if user.created_at else None
        })
    return result

@router.put("/admin/users/{user_id}")
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    """Update a user"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.name is not None:
        db_user.name = user.name
    if user.email is not None:
        db_user.email = user.email
    if user.readiness_score is not None:
        db_user.readiness_score = user.readiness_score
    if user.technical_score is not None:
        db_user.technical_score = user.technical_score
    if user.soft_skills_score is not None:
        db_user.soft_skills_score = user.soft_skills_score
    if user.preferred_specialization_id is not None:
        db_user.preferred_specialization_id = user.preferred_specialization_id
    
    db.commit()
    db.refresh(db_user)
    return {"success": True, "message": "User updated"}

# ============================================================
# STATISTICS
# ============================================================

@router.get("/admin/stats")
def get_statistics(db: Session = Depends(get_db)):
    """Get database statistics"""
    from sqlalchemy import func
    
    return {
        "sectors": db.query(models.Sector).count(),
        "active_sectors": db.query(models.Sector).filter(models.Sector.is_active == True).count(),
        "branches": db.query(models.Branch).count(),
        "active_branches": db.query(models.Branch).filter(models.Branch.is_active == True).count(),
        "specializations": db.query(models.Specialization).count(),
        "active_specializations": db.query(models.Specialization).filter(models.Specialization.is_active == True).count(),
        "quizzes": db.query(models.Quiz).count(),
        "users": db.query(models.User).count(),
        "active_users": db.query(models.User).filter(models.User.is_active == True).count(),
        "quiz_attempts": db.query(models.QuizAttempt).count(),
        "avg_readiness_score": db.query(func.avg(models.User.readiness_score)).scalar() or 0.0
    }

