from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from .. import crud, schemas
from .. import models_hierarchical as models
from ..database import get_db

router = APIRouter()

# Simple request models
class UserRegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class UserLoginRequest(BaseModel):
    email: str
    password: str

class UserUpdateRequest(BaseModel):
    specialization_id: int

# ENDPOINTS
@router.post("/register")
def register(data: UserRegisterRequest, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_email(db, data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = crud.create_user(
        db=db,
        email=data.email,
        password=data.password,
        name=data.name
    )
    
    return {
        "success": True,
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "name": new_user.name,
            "readiness_score": new_user.readiness_score,
            "technical_score": new_user.technical_score,
            "soft_skills_score": new_user.soft_skills_score,
            "created_at": str(new_user.created_at)
        }
    }

@router.post("/login")
def login(data: UserLoginRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, data.email)
    
    if not user or user.password_hash != data.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    return {
        "success": True,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "readiness_score": user.readiness_score,
            "technical_score": user.technical_score,
            "soft_skills_score": user.soft_skills_score,
            "created_at": str(user.created_at)
        }
    }

@router.patch("/users/{user_id}/specialization")
def update_specialization(user_id: int, data: UserUpdateRequest, db: Session = Depends(get_db)):
    if data.specialization_id is None:
        raise HTTPException(status_code=400, detail="Specialization ID is required")
    
    user = crud.update_user_specialization(db, user_id, data.specialization_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "success": True,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "specialization_id": user.preferred_specialization_id
        }
    }

@router.get("/users/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "specialization_id": user.preferred_specialization_id,
        "readiness_score": user.readiness_score,
        "technical_score": user.technical_score,
        "soft_skills_score": user.soft_skills_score,
        "leadership_score": user.leadership_score,
        "created_at": user.created_at
    }

@router.get("/sectors", response_model=schemas.SectorsResponse)
def get_sectors(db: Session = Depends(get_db)):
    sectors = crud.get_all_sectors(db)
    return {
        "sectors": [
            {
                "id": sector.id,
                "name": sector.name,
                "description": sector.description
            } for sector in sectors
        ]
    }

@router.get("/sectors/{sector_id}/branches")
def get_branches_by_sector(sector_id: int, db: Session = Depends(get_db)):
    branches = crud.get_branches_by_sector(db, sector_id)
    return {
        "branches": [
            {
                "id": branch.id,
                "name": branch.name,
                "description": branch.description,
                "sector_id": branch.sector_id
            } for branch in branches
        ]
    }

@router.get("/branches/{branch_id}/specializations")  
def get_specializations_by_branch(branch_id: int, db: Session = Depends(get_db)):
    specializations = crud.get_specializations_by_branch(db, branch_id)
    return {
        "specializations": [
            {
                "id": spec.id,
                "name": spec.name,
                "description": spec.description,
                "branch_id": spec.branch_id
            } for spec in specializations
        ]
    }
