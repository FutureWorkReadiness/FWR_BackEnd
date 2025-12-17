"""
Base seed functionality.
Provides utilities for loading data from JSON files and running seeds.
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from src.app.db.session import SessionLocal

# Path to data directory
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_json_file(filename: str) -> Optional[Dict[str, Any]]:
    """Load data from a JSON file in the data directory."""
    file_path = DATA_DIR / filename
    if not file_path.exists():
        print(f"⚠️  JSON file not found: {file_path}")
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON file {filename}: {e}")
        return None


def get_db_session() -> Session:
    """Get a database session for seeding."""
    return SessionLocal()


def run_all_seeds(force: bool = False) -> None:
    """
    Run all seed scripts in order.

    Args:
        force: If True, will re-seed even if data exists
    """
    from seeds.seed_sectors import seed_sectors
    from seeds.seed_quizzes import seed_quizzes

    print("🌱 Starting database seeding...")

    # Run seeds in order (sectors must be created before quizzes)
    seed_sectors(force=force)
    seed_quizzes(force=force)

    print("✅ All seeds completed!")


def auto_seed_if_empty() -> None:
    """
    Automatically run seeds if the database is empty.
    Called during application startup.
    """
    from src.app.modules.sectors.models import Sector

    db = get_db_session()
    try:
        sector_count = db.query(Sector).count()

        if sector_count == 0:
            print("📊 Database is empty. Running auto-seed...")
            run_all_seeds(force=False)
        else:
            print(f"✅ Database already seeded: {sector_count} sector(s) found")
    except Exception as e:
        print(f"⚠️  Error checking database: {e}")
    finally:
        db.close()

