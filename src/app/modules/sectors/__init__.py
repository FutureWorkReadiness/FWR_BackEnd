"""
Sectors module.
Handles sector, branch, and specialization domain logic.
"""

from src.app.modules.sectors.models import Sector, Branch, Specialization
from src.app.modules.sectors.service import SectorService

__all__ = ["Sector", "Branch", "Specialization", "SectorService"]

