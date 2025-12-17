"""
Database package.
Provides database configuration, session management, base model, and model registry.
"""

from src.app.db.base import Base
from src.app.db.session import engine, SessionLocal, get_db

# Import all models to register them with Base
# This ensures all models are available when importing from src.app.db
from src.app.db.models import *

__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
    # Re-export all models
    "Sector",
    "Branch",
    "Specialization",
    "Quiz",
    "Question",
    "QuestionOption",
    "QuizAttempt",
    "User",
    "PeerBenchmark",
    "Badge",
    "UserBadge",
    "Goal",
    "JournalEntry",
]
