"""
Hierarchical API endpoints for 3-level sector structure: Sector -> Branch -> Specialization
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..models.models_hierarchical import Sector, Branch, Specialization
from ..database import get_db


router = APIRouter()

@router.get("/sectors", response_model=List[dict])
def get_sectors(db: Session = Depends(get_db)):
    """Get all sectors"""
    try:
        sectors = db.query(Sector).filter(Sector.is_active == True).all()
        result = []
        
        for sector in sectors:
            sector_data = {
                "id": sector.id,
                "name": sector.name,
                "description": sector.description,
                "created_at": sector.created_at.isoformat() if sector.created_at else None
            }
            result.append(sector_data)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sectors: {str(e)}")


@router.get("/sectors/{sector_id}", response_model=dict)
def get_sector_by_id(sector_id: int, db: Session = Depends(get_db)):
    """Get a specific sector by ID"""
    try:
        sector = db.query(Sector).filter(Sector.id == sector_id, Sector.is_active == True).first()
        if not sector:
            raise HTTPException(status_code=404, detail="Sector not found")
        
        return {
            "id": sector.id,
            "name": sector.name,
            "description": sector.description,
            "created_at": sector.created_at.isoformat() if sector.created_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sector: {str(e)}")


@router.get("/sectors/{sector_id}/branches", response_model=List[dict])
def get_branches_by_sector(sector_id: int, db: Session = Depends(get_db)):
    """Get all branches for a specific sector"""
    try:
        # First check if sector exists
        sector = db.query(Sector).filter(Sector.id == sector_id, Sector.is_active == True).first()
        if not sector:
            raise HTTPException(status_code=404, detail="Sector not found")
        
        branches = db.query(Branch).filter(
            Branch.sector_id == sector_id,
            Branch.is_active == True
        ).all()
        
        result = []
        for branch in branches:
            branch_data = {
                "id": branch.id,
                "name": branch.name,
                "description": branch.description,
                "sector_id": branch.sector_id,
                "created_at": branch.created_at.isoformat() if branch.created_at else None
            }
            result.append(branch_data)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching branches: {str(e)}")


@router.get("/branches/{branch_id}", response_model=dict)
def get_branch_by_id(branch_id: int, db: Session = Depends(get_db)):
    """Get a specific branch by ID"""
    try:
        branch = db.query(Branch).filter(Branch.id == branch_id, Branch.is_active == True).first()
        if not branch:
            raise HTTPException(status_code=404, detail="Branch not found")
        
        return {
            "id": branch.id,
            "name": branch.name,
            "description": branch.description,
            "sector_id": branch.sector_id,
            "created_at": branch.created_at.isoformat() if branch.created_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching branch: {str(e)}")


@router.get("/branches/{branch_id}/specializations", response_model=List[dict])
def get_specializations_by_branch(branch_id: int, db: Session = Depends(get_db)):
    """Get all specializations for a specific branch"""
    try:
        # First check if branch exists
        branch = db.query(Branch).filter(Branch.id == branch_id, Branch.is_active == True).first()
        if not branch:
            raise HTTPException(status_code=404, detail="Branch not found")
        
        specializations = db.query(Specialization).filter(
            Specialization.branch_id == branch_id,
            Specialization.is_active == True
        ).all()
        
        result = []
        for spec in specializations:
            spec_data = {
                "id": spec.id,
                "name": spec.name,
                "description": spec.description,
                "branch_id": spec.branch_id,
                "created_at": spec.created_at.isoformat() if spec.created_at else None
            }
            result.append(spec_data)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching specializations: {str(e)}")


@router.get("/specializations/{specialization_id}", response_model=dict)
def get_specialization_by_id(specialization_id: int, db: Session = Depends(get_db)):
    """Get a specific specialization by ID"""
    try:
        specialization = db.query(Specialization).filter(
            Specialization.id == specialization_id, 
            Specialization.is_active == True
        ).first()
        if not specialization:
            raise HTTPException(status_code=404, detail="Specialization not found")
        
        return {
            "id": specialization.id,
            "name": specialization.name,
            "description": specialization.description,
            "branch_id": specialization.branch_id,
            "created_at": specialization.created_at.isoformat() if specialization.created_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching specialization: {str(e)}")


@router.get("/sectors/{sector_id}/hierarchy", response_model=dict)
def get_sector_full_hierarchy(sector_id: int, db: Session = Depends(get_db)):
    """Get the complete hierarchy for a sector (sector -> branches -> specializations)"""
    try:
        # First check if sector exists
        sector = db.query(Sector).filter(Sector.id == sector_id, Sector.is_active == True).first()
        if not sector:
            raise HTTPException(status_code=404, detail="Sector not found")
        
        # Get all branches for this sector
        branches = db.query(Branch).filter(
            Branch.sector_id == sector_id,
            Branch.is_active == True
        ).all()
        
        branches_data = []
        for branch in branches:
            # Get all specializations for this branch
            specializations = db.query(Specialization).filter(
                Specialization.branch_id == branch.id,
                Specialization.is_active == True
            ).all()
            
            specializations_data = []
            for spec in specializations:
                specializations_data.append({
                    "id": spec.id,
                    "name": spec.name,
                    "description": spec.description
                })
            
            branches_data.append({
                "id": branch.id,
                "name": branch.name,
                "description": branch.description,
                "specializations": specializations_data
            })
        
        return {
            "id": sector.id,
            "name": sector.name,
            "description": sector.description,
            "branches": branches_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sector hierarchy: {str(e)}")


@router.get("/hierarchy", response_model=List[dict])
def get_complete_hierarchy(db: Session = Depends(get_db)):
    """Get the complete hierarchy for all sectors"""
    try:
        sectors = db.query(Sector).filter(Sector.is_active == True).all()
        result = []
        
        for sector in sectors:
            # Get all branches for this sector
            branches = db.query(Branch).filter(
                Branch.sector_id == sector.id,
                Branch.is_active == True
            ).all()
            
            branches_data = []
            for branch in branches:
                # Get all specializations for this branch
                specializations = db.query(Specialization).filter(
                    Specialization.branch_id == branch.id,
                    Specialization.is_active == True
                ).all()
                
                specializations_data = []
                for spec in specializations:
                    specializations_data.append({
                        "id": spec.id,
                        "name": spec.name,
                        "description": spec.description
                    })
                
                branches_data.append({
                    "id": branch.id,
                    "name": branch.name,
                    "description": branch.description,
                    "specializations": specializations_data
                })
            
            result.append({
                "id": sector.id,
                "name": sector.name,
                "description": sector.description,
                "branches": branches_data
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching complete hierarchy: {str(e)}")
