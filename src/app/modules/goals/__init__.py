"""
Goals module.
Handles goal and journal entry domain logic.
"""

from src.app.modules.goals.models import Goal, JournalEntry
from src.app.modules.goals.service import GoalService

__all__ = ["Goal", "JournalEntry", "GoalService"]

