"""
Sector, Branch, and Specialization schemas.
Pydantic models for the industry hierarchy: Sector → Branch → Specialization
"""

from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID


# ============================================================
# SECTOR SCHEMAS
# ============================================================


class SectorBase(BaseModel):
    """Base schema for Sector data."""

    name: str
    description: Optional[str] = None


class SectorCreate(SectorBase):
    """Schema for creating a new Sector."""

    pass


class Sector(SectorBase):
    """Schema for Sector response."""

    sector_id: UUID

    class Config:
        from_attributes = True


class SectorsResponse(BaseModel):
    """Response schema for list of sectors."""

    sectors: List[Sector]


# ============================================================
# BRANCH SCHEMAS
# ============================================================


class BranchBase(BaseModel):
    """Base schema for Branch data."""

    name: str
    description: Optional[str] = None
    sector_id: UUID


class BranchCreate(BranchBase):
    """Schema for creating a new Branch."""

    pass


class Branch(BranchBase):
    """Schema for Branch response."""

    branch_id: UUID

    class Config:
        from_attributes = True


class BranchesResponse(BaseModel):
    """Response schema for list of branches."""

    branches: List[Branch]


# ============================================================
# SPECIALIZATION SCHEMAS
# ============================================================


class SpecializationBase(BaseModel):
    """Base schema for Specialization data."""

    name: str
    description: Optional[str] = None
    branch_id: UUID


class SpecializationCreate(SpecializationBase):
    """Schema for creating a new Specialization."""

    pass


class Specialization(SpecializationBase):
    """Schema for Specialization response."""

    specialization_id: UUID

    class Config:
        from_attributes = True


class SpecializationsResponse(BaseModel):
    """Response schema for list of specializations."""

    specializations: List[Specialization]


# ============================================================
# HIERARCHY SCHEMAS (for nested responses)
# ============================================================


class SpecializationInBranch(BaseModel):
    """Specialization schema when nested in Branch."""

    specialization_id: UUID
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class BranchWithSpecializations(BaseModel):
    """Branch schema with nested specializations."""

    branch_id: UUID
    name: str
    description: Optional[str] = None
    specializations: List[SpecializationInBranch] = []

    class Config:
        from_attributes = True


class SectorWithBranches(BaseModel):
    """Sector schema with nested branches and specializations."""

    sector_id: UUID
    name: str
    description: Optional[str] = None
    branches: List[BranchWithSpecializations] = []

    class Config:
        from_attributes = True


class HierarchyResponse(BaseModel):
    """Response schema for complete hierarchy."""

    sectors: List[SectorWithBranches]

