"""
Models Registry - Central import point for all SQLAlchemy models.

When adding new models:
1. Create your model in the appropriate module (e.g., src/app/modules/your_module/models.py)
2. Import it here
3. Add it to __all__

This file is used by:
- Alembic (for migrations)
- Bootstrap (for table creation)
- Docker scripts (for table creation)
"""

from src.app.db.base import Base

# Sector hierarchy models
from src.app.modules.sectors.models import Sector, Branch, Specialization

# Quiz system models
from src.app.modules.quizzes.models import Quiz, Question, QuestionOption, QuizAttempt

# User models
from src.app.modules.users.models import User

# Benchmark models
from src.app.modules.benchmarks.models import PeerBenchmark

# Badge models
from src.app.modules.badges.models import Badge, UserBadge

# Goal & Journal models
from src.app.modules.goals.models import Goal, JournalEntry

# Quiz Generator models
from src.app.modules.quiz_generator.models import GenerationJob

# Export all models
__all__ = [
    "Base",
    # Sectors
    "Sector",
    "Branch",
    "Specialization",
    # Quizzes
    "Quiz",
    "Question",
    "QuestionOption",
    "QuizAttempt",
    # Users
    "User",
    # Benchmarks
    "PeerBenchmark",
    # Badges
    "Badge",
    "UserBadge",
    # Goals
    "Goal",
    "JournalEntry",
    # Quiz Generator
    "GenerationJob",
]
