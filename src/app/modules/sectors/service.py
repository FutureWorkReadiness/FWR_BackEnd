"""
Sector service - handles sector, branch, and specialization business logic.
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from src.app.modules.sectors.models import Sector, Branch, Specialization


class SectorService:
    """Service class for sector-related operations."""

    # ============================================================
    # SECTOR OPERATIONS
    # ============================================================

    @staticmethod
    def get_all_sectors(db: Session, active_only: bool = True) -> List[Sector]:
        """Get all sectors."""
        query = db.query(Sector)
        if active_only:
            query = query.filter(Sector.is_active == True)
        return query.all()

    @staticmethod
    def get_sector_by_id(db: Session, sector_id: UUID, active_only: bool = True) -> Optional[Sector]:
        """Get a sector by ID."""
        query = db.query(Sector).filter(Sector.sector_id == sector_id)
        if active_only:
            query = query.filter(Sector.is_active == True)
        return query.first()

    @staticmethod
    def create_sector(db: Session, name: str, description: Optional[str] = None) -> Sector:
        """Create a new sector."""
        sector = Sector(name=name, description=description)
        db.add(sector)
        db.commit()
        db.refresh(sector)
        return sector

    @staticmethod
    def update_sector(
        db: Session,
        sector_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[Sector]:
        """Update a sector."""
        sector = db.query(Sector).filter(Sector.sector_id == sector_id).first()
        if not sector:
            return None

        if name is not None:
            sector.name = name
        if description is not None:
            sector.description = description
        if is_active is not None:
            sector.is_active = is_active

        db.commit()
        db.refresh(sector)
        return sector

    @staticmethod
    def delete_sector(db: Session, sector_id: UUID, soft_delete: bool = True) -> bool:
        """Delete a sector (soft delete by default)."""
        sector = db.query(Sector).filter(Sector.sector_id == sector_id).first()
        if not sector:
            return False

        if soft_delete:
            sector.is_active = False
        else:
            db.delete(sector)

        db.commit()
        return True

    @staticmethod
    def get_sector_branch_count(db: Session, sector_id: UUID) -> int:
        """Get the count of branches in a sector."""
        return db.query(Branch).filter(Branch.sector_id == sector_id).count()

    # ============================================================
    # BRANCH OPERATIONS
    # ============================================================

    @staticmethod
    def get_branches_by_sector(db: Session, sector_id: UUID, active_only: bool = True) -> List[Branch]:
        """Get all branches for a sector."""
        query = db.query(Branch).filter(Branch.sector_id == sector_id)
        if active_only:
            query = query.filter(Branch.is_active == True)
        return query.all()

    @staticmethod
    def get_all_branches(db: Session, sector_id: Optional[UUID] = None, active_only: bool = False) -> List[Branch]:
        """Get all branches, optionally filtered by sector."""
        query = db.query(Branch)
        if sector_id:
            query = query.filter(Branch.sector_id == sector_id)
        if active_only:
            query = query.filter(Branch.is_active == True)
        return query.all()

    @staticmethod
    def get_branch_by_id(db: Session, branch_id: UUID, active_only: bool = True) -> Optional[Branch]:
        """Get a branch by ID."""
        query = db.query(Branch).filter(Branch.branch_id == branch_id)
        if active_only:
            query = query.filter(Branch.is_active == True)
        return query.first()

    @staticmethod
    def create_branch(db: Session, name: str, sector_id: UUID, description: Optional[str] = None) -> Branch:
        """Create a new branch."""
        branch = Branch(name=name, sector_id=sector_id, description=description)
        db.add(branch)
        db.commit()
        db.refresh(branch)
        return branch

    @staticmethod
    def update_branch(
        db: Session,
        branch_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        sector_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[Branch]:
        """Update a branch."""
        branch = db.query(Branch).filter(Branch.branch_id == branch_id).first()
        if not branch:
            return None

        if name is not None:
            branch.name = name
        if description is not None:
            branch.description = description
        if sector_id is not None:
            branch.sector_id = sector_id
        if is_active is not None:
            branch.is_active = is_active

        db.commit()
        db.refresh(branch)
        return branch

    @staticmethod
    def delete_branch(db: Session, branch_id: UUID, soft_delete: bool = True) -> bool:
        """Delete a branch (soft delete by default)."""
        branch = db.query(Branch).filter(Branch.branch_id == branch_id).first()
        if not branch:
            return False

        if soft_delete:
            branch.is_active = False
        else:
            db.delete(branch)

        db.commit()
        return True

    @staticmethod
    def get_branch_specialization_count(db: Session, branch_id: UUID) -> int:
        """Get the count of specializations in a branch."""
        return db.query(Specialization).filter(Specialization.branch_id == branch_id).count()

    # ============================================================
    # SPECIALIZATION OPERATIONS
    # ============================================================

    @staticmethod
    def get_specializations_by_branch(db: Session, branch_id: UUID, active_only: bool = True) -> List[Specialization]:
        """Get all specializations for a branch."""
        query = db.query(Specialization).filter(Specialization.branch_id == branch_id)
        if active_only:
            query = query.filter(Specialization.is_active == True)
        return query.all()

    @staticmethod
    def get_specializations_by_sector(db: Session, sector_id: UUID) -> List[Specialization]:
        """Get all specializations for a sector (through branches)."""
        branches = SectorService.get_branches_by_sector(db, sector_id)
        branch_ids = [branch.branch_id for branch in branches]
        if not branch_ids:
            return []
        return db.query(Specialization).filter(Specialization.branch_id.in_(branch_ids)).all()

    @staticmethod
    def get_all_specializations(
        db: Session,
        branch_id: Optional[UUID] = None,
        active_only: bool = False,
    ) -> List[Specialization]:
        """Get all specializations, optionally filtered by branch."""
        query = db.query(Specialization)
        if branch_id:
            query = query.filter(Specialization.branch_id == branch_id)
        if active_only:
            query = query.filter(Specialization.is_active == True)
        return query.all()

    @staticmethod
    def get_specialization_by_id(
        db: Session, specialization_id: UUID, active_only: bool = True
    ) -> Optional[Specialization]:
        """Get a specialization by ID."""
        query = db.query(Specialization).filter(Specialization.specialization_id == specialization_id)
        if active_only:
            query = query.filter(Specialization.is_active == True)
        return query.first()

    @staticmethod
    def get_specialization_by_name(db: Session, name: str) -> Optional[Specialization]:
        """Get a specialization by name."""
        return db.query(Specialization).filter(Specialization.name == name).first()

    @staticmethod
    def create_specialization(
        db: Session,
        name: str,
        branch_id: UUID,
        description: Optional[str] = None,
    ) -> Specialization:
        """Create a new specialization."""
        specialization = Specialization(
            name=name,
            branch_id=branch_id,
            description=description,
        )
        db.add(specialization)
        db.commit()
        db.refresh(specialization)
        return specialization

    @staticmethod
    def update_specialization(
        db: Session,
        specialization_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        branch_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[Specialization]:
        """Update a specialization."""
        specialization = db.query(Specialization).filter(
            Specialization.specialization_id == specialization_id
        ).first()
        if not specialization:
            return None

        if name is not None:
            specialization.name = name
        if description is not None:
            specialization.description = description
        if branch_id is not None:
            specialization.branch_id = branch_id
        if is_active is not None:
            specialization.is_active = is_active

        db.commit()
        db.refresh(specialization)
        return specialization

    @staticmethod
    def delete_specialization(db: Session, specialization_id: UUID, soft_delete: bool = True) -> bool:
        """Delete a specialization (soft delete by default)."""
        specialization = db.query(Specialization).filter(
            Specialization.specialization_id == specialization_id
        ).first()
        if not specialization:
            return False

        if soft_delete:
            specialization.is_active = False
        else:
            db.delete(specialization)

        db.commit()
        return True

    # ============================================================
    # HIERARCHY OPERATIONS
    # ============================================================

    @staticmethod
    def get_sector_hierarchy(db: Session, sector_id: UUID) -> Optional[dict]:
        """Get the complete hierarchy for a sector."""
        sector = SectorService.get_sector_by_id(db, sector_id)
        if not sector:
            return None

        branches = SectorService.get_branches_by_sector(db, sector_id)
        branches_data = []

        for branch in branches:
            specializations = SectorService.get_specializations_by_branch(db, branch.branch_id)
            specializations_data = [
                {
                    "specialization_id": str(spec.specialization_id),
                    "name": spec.name,
                    "description": spec.description,
                }
                for spec in specializations
            ]

            branches_data.append({
                "branch_id": str(branch.branch_id),
                "name": branch.name,
                "description": branch.description,
                "specializations": specializations_data,
            })

        return {
            "sector_id": str(sector.sector_id),
            "name": sector.name,
            "description": sector.description,
            "branches": branches_data,
        }

    @staticmethod
    def get_complete_hierarchy(db: Session) -> List[dict]:
        """Get the complete hierarchy for all sectors."""
        sectors = SectorService.get_all_sectors(db)
        result = []

        for sector in sectors:
            hierarchy = SectorService.get_sector_hierarchy(db, sector.sector_id)
            if hierarchy:
                result.append(hierarchy)

        return result

