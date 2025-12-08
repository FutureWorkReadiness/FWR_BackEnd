from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..models import models_hierarchical as models
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
            "specialization_id": new_user.preferred_specialization_id,
            "readiness_score": new_user.readiness_score,
            "technical_score": new_user.technical_score,
            "soft_skills_score": new_user.soft_skills_score,
            "leadership_score": new_user.leadership_score,
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
            "specialization_id": user.preferred_specialization_id,
            "readiness_score": user.readiness_score,
            "technical_score": user.technical_score,
            "soft_skills_score": user.soft_skills_score,
            "leadership_score": user.leadership_score,
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


@router.get("/users/{user_id}/peer-benchmark", response_model=schemas.PeerBenchmarkResponse)
def get_peer_benchmark_endpoint(user_id: int, db: Session = Depends(get_db)):
    """
    Get peer benchmarking data comparing user's scores with peers in their specialization
    """
    from datetime import datetime
    
    # Get peer benchmark data using the improved CRUD function
    data = crud.get_peer_benchmark(db, user_id)
    
    if not data:
        raise HTTPException(
            status_code=404, 
            detail="User not found or no specialization set. Please complete onboarding first."
        )
    
    # Check if there's an error (not enough users)
    if "error" in data:
        raise HTTPException(
            status_code=400,
            detail=data.get("message", "Not enough data for peer comparison")
        )
    
    # Data is already in the correct format from the CRUD function
    return {
        "success": True,
        "data": {
            "specialization_name": data["specialization_name"],
            "total_peers": data["total_peers"],
            "comparisons": data["comparisons"],
            "overall_percentile": data["overall_percentile"],
            "common_strengths": data["common_strengths"],
            "common_gaps": data["common_gaps"],
            "last_updated": data.get("last_updated") or datetime.now().isoformat()
        }
    }
