"""
Sector API endpoints.
Hierarchical structure: Sector -> Branch -> Specialization
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from src.app.db.session import get_db
from src.app.modules.sectors.service import SectorService

router = APIRouter()


# ============================================================
# SECTOR ENDPOINTS
# ============================================================


@router.get("/", response_model=List[dict])
def get_sectors(db: Session = Depends(get_db)):
    """Get all sectors."""
    try:
        sectors = SectorService.get_all_sectors(db, active_only=True)
        result = []

        for sector in sectors:
            sector_data = {
                "sector_id": str(sector.sector_id),
                "name": sector.name,
                "description": sector.description,
                "created_at": sector.created_at.isoformat() if sector.created_at else None,
            }
            result.append(sector_data)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sectors: {str(e)}")


@router.get("/hierarchy", response_model=List[dict])
def get_complete_hierarchy(db: Session = Depends(get_db)):
    """Get the complete hierarchy for all sectors."""
    try:
        return SectorService.get_complete_hierarchy(db)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching complete hierarchy: {str(e)}")


@router.get("/{sector_id}", response_model=dict)
def get_sector_by_id(sector_id: UUID, db: Session = Depends(get_db)):
    """Get a specific sector by ID."""
    try:
        sector = SectorService.get_sector_by_id(db, sector_id, active_only=True)
        if not sector:
            raise HTTPException(status_code=404, detail="Sector not found")

        return {
            "sector_id": str(sector.sector_id),
            "name": sector.name,
            "description": sector.description,
            "created_at": sector.created_at.isoformat() if sector.created_at else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sector: {str(e)}")


@router.get("/{sector_id}/branches", response_model=List[dict])
def get_branches_by_sector(sector_id: UUID, db: Session = Depends(get_db)):
    """Get all branches for a specific sector."""
    try:
        sector = SectorService.get_sector_by_id(db, sector_id, active_only=True)
        if not sector:
            raise HTTPException(status_code=404, detail="Sector not found")

        branches = SectorService.get_branches_by_sector(db, sector_id, active_only=True)

        result = []
        for branch in branches:
            branch_data = {
                "branch_id": str(branch.branch_id),
                "name": branch.name,
                "description": branch.description,
                "sector_id": str(branch.sector_id),
                "created_at": branch.created_at.isoformat() if branch.created_at else None,
            }
            result.append(branch_data)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching branches: {str(e)}")


@router.get("/{sector_id}/hierarchy", response_model=dict)
def get_sector_full_hierarchy(sector_id: UUID, db: Session = Depends(get_db)):
    """Get the complete hierarchy for a sector (sector -> branches -> specializations)."""
    try:
        hierarchy = SectorService.get_sector_hierarchy(db, sector_id)
        if not hierarchy:
            raise HTTPException(status_code=404, detail="Sector not found")

        return hierarchy

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sector hierarchy: {str(e)}")


# ============================================================
# BRANCH ENDPOINTS
# ============================================================


@router.get("/branches/{branch_id}", response_model=dict)
def get_branch_by_id(branch_id: UUID, db: Session = Depends(get_db)):
    """Get a specific branch by ID."""
    try:
        branch = SectorService.get_branch_by_id(db, branch_id, active_only=True)
        if not branch:
            raise HTTPException(status_code=404, detail="Branch not found")

        return {
            "branch_id": str(branch.branch_id),
            "name": branch.name,
            "description": branch.description,
            "sector_id": str(branch.sector_id),
            "created_at": branch.created_at.isoformat() if branch.created_at else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching branch: {str(e)}")


@router.get("/branches/{branch_id}/specializations", response_model=List[dict])
def get_specializations_by_branch(branch_id: UUID, db: Session = Depends(get_db)):
    """Get all specializations for a specific branch."""
    try:
        branch = SectorService.get_branch_by_id(db, branch_id, active_only=True)
        if not branch:
            raise HTTPException(status_code=404, detail="Branch not found")

        specializations = SectorService.get_specializations_by_branch(db, branch_id, active_only=True)

        result = []
        for spec in specializations:
            spec_data = {
                "specialization_id": str(spec.specialization_id),
                "name": spec.name,
                "description": spec.description,
                "branch_id": str(spec.branch_id),
                "created_at": spec.created_at.isoformat() if spec.created_at else None,
            }
            result.append(spec_data)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching specializations: {str(e)}")


# ============================================================
# SPECIALIZATION ENDPOINTS
# ============================================================


@router.get("/specializations/{specialization_id}", response_model=dict)
def get_specialization_by_id(specialization_id: UUID, db: Session = Depends(get_db)):
    """Get a specific specialization by ID."""
    try:
        specialization = SectorService.get_specialization_by_id(db, specialization_id, active_only=True)
        if not specialization:
            raise HTTPException(status_code=404, detail="Specialization not found")

        return {
            "specialization_id": str(specialization.specialization_id),
            "name": specialization.name,
            "description": specialization.description,
            "branch_id": str(specialization.branch_id),
            "created_at": specialization.created_at.isoformat() if specialization.created_at else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching specialization: {str(e)}")

