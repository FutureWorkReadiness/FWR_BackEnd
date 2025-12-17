"""
Seeds package.
Contains database seed scripts for populating initial data.
"""

from seeds.base import run_all_seeds, auto_seed_if_empty
from seeds.seed_sectors import seed_sectors
from seeds.seed_quizzes import seed_quizzes

__all__ = [
    "run_all_seeds",
    "auto_seed_if_empty",
    "seed_sectors",
    "seed_quizzes",
]

