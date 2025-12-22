"""
Seed quizzes and questions.
Loads data from data/generated_sectors/ directory.

Each sector file (e.g., education.json, technology.json) contains
quizzes for all specializations in that sector.

New format (v2):
- Questions have question_text, question_type, points, explanation
- Options have key (A-E), text, is_correct, rationale
- 5 options per question
"""

import os
import json
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func

from seeds.base import get_db_session
from src.app.modules.sectors.models import Specialization
from src.app.modules.quizzes.models import Quiz, Question, QuestionOption


# Path to generated sectors directory
GENERATED_SECTORS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "generated_sectors"
)


def load_sector_file(sector_name: str) -> Optional[Dict[str, Any]]:
    """Load a sector's quiz data from generated_sectors directory."""
    file_path = os.path.join(GENERATED_SECTORS_DIR, f"{sector_name}.json")

    if not os.path.exists(file_path):
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing {file_path}: {e}")
        return None


def get_all_sector_files() -> List[str]:
    """Get list of all sector JSON files in generated_sectors directory."""
    if not os.path.exists(GENERATED_SECTORS_DIR):
        print(f"⚠️  Directory not found: {GENERATED_SECTORS_DIR}")
        return []

    files = []
    for filename in os.listdir(GENERATED_SECTORS_DIR):
        if filename.endswith(".json") and filename != ".gitkeep":
            # Extract sector name (remove .json extension)
            sector_name = filename[:-5]
            files.append(sector_name)

    return sorted(files)


def normalize_specialization_name(name: str) -> str:
    """
    Normalize specialization name for matching.
    Converts to uppercase and handles common variations.

    Examples:
        'special_need_educator' -> 'SPECIAL_NEED_EDUCATOR'
        'teacher' -> 'TEACHER'
    """
    return name.upper().strip()


def find_specialization(db: Session, spec_name: str) -> Optional[Specialization]:
    """
    Find a specialization by name (case-insensitive).

    The generated quizzes use lowercase_snake_case but the database
    stores UPPER_SNAKE_CASE, so we normalize before matching.
    """
    normalized = normalize_specialization_name(spec_name)

    # Try exact match first (case-insensitive)
    specialization = (
        db.query(Specialization)
        .filter(func.upper(Specialization.name) == normalized)
        .first()
    )

    return specialization


def seed_quizzes(force: bool = False) -> None:
    """
    Seed quizzes and questions from generated sector files.

    Args:
        force: If True, will add missing quizzes even if some exist
    """
    db = get_db_session()

    try:
        # Check if quizzes already exist
        existing_count = db.query(Quiz).count()

        if existing_count > 0 and not force:
            print(f"✅ Quizzes already seeded: {existing_count} quiz(zes) found")
            print("   Use --force to add additional quizzes")
            return

        # Get all sector files
        sector_files = get_all_sector_files()

        if not sector_files:
            print("⚠️  No sector files found in data/generated_sectors/")
            print(f"   Looking in: {GENERATED_SECTORS_DIR}")
            return

        print(f"📂 Found {len(sector_files)} sector file(s): {', '.join(sector_files)}")

        total_quizzes_added = 0
        total_questions_added = 0
        total_skipped = 0

        for sector_name in sector_files:
            print(f"\n📁 Processing sector: {sector_name}")

            data = load_sector_file(sector_name)
            if not data:
                print(f"   ⚠️  Could not load {sector_name}.json")
                continue

            quizzes_data = data.get("quizzes", [])
            if not quizzes_data:
                print(f"   ⚠️  No quizzes found in {sector_name}.json")
                continue

            print(f"   📝 Found {len(quizzes_data)} quiz(zes)")

            added_quizzes = 0
            added_questions = 0
            skipped_quizzes = 0

            for quiz_data in quizzes_data:
                spec_name = quiz_data.get("specialization", "")

                # Find specialization by name
                specialization = find_specialization(db, spec_name)

                if not specialization:
                    print(
                        f"   ⚠️  Specialization '{spec_name}' not found, skipping quiz: {quiz_data.get('title', 'Unknown')}"
                    )
                    skipped_quizzes += 1
                    continue

                # Check if quiz already exists
                existing_quiz = (
                    db.query(Quiz)
                    .filter(
                        Quiz.title == quiz_data["title"],
                        Quiz.specialization_id == specialization.specialization_id,
                    )
                    .first()
                )

                if existing_quiz:
                    # Skip silently to avoid too much output
                    continue

                # Create quiz
                quiz = Quiz(
                    title=quiz_data["title"],
                    description=quiz_data.get("description", ""),
                    specialization_id=specialization.specialization_id,
                    difficulty_level=quiz_data.get("difficulty_level", 1),
                    time_limit_minutes=quiz_data.get("time_limit_minutes", 30),
                    passing_score=quiz_data.get("passing_score", 70.0),
                )
                db.add(quiz)
                db.commit()
                db.refresh(quiz)
                added_quizzes += 1

                # Create questions
                questions_added = _seed_quiz_questions(
                    db, quiz.quiz_id, quiz_data.get("questions", [])
                )
                added_questions += questions_added

            print(f"   ✅ Added {added_quizzes} quiz(zes), {added_questions} questions")
            if skipped_quizzes > 0:
                print(
                    f"   ⚠️  Skipped {skipped_quizzes} quiz(zes) (missing specialization)"
                )

            total_quizzes_added += added_quizzes
            total_questions_added += added_questions
            total_skipped += skipped_quizzes

        print(f"\n{'='*60}")
        print(f"✅ Quiz seeding complete!")
        print(f"   - Total quizzes added: {total_quizzes_added}")
        print(f"   - Total questions added: {total_questions_added}")
        if total_skipped > 0:
            print(f"   - Total skipped (missing specialization): {total_skipped}")

    except Exception as e:
        print(f"❌ Error seeding quizzes: {e}")
        import traceback

        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


def _seed_quiz_questions(
    db: Session, quiz_id: UUID, questions_data: List[Dict[str, Any]]
) -> int:
    """
    Seed questions for a quiz using the new format.

    New format expects:
    - question_text: str
    - question_type: str (default: 'multiple_choice')
    - points: int (default: 1)
    - explanation: str
    - options: List with key, text, is_correct, rationale

    Returns:
        Number of questions added
    """
    added = 0

    for idx, q_data in enumerate(questions_data):
        question_text = q_data.get("question_text", "")

        if not question_text:
            continue

        question = Question(
            quiz_id=quiz_id,
            question_text=question_text,
            question_type=q_data.get("question_type", "multiple_choice"),
            points=q_data.get("points", 1),
            order_index=idx + 1,
            explanation=q_data.get("explanation"),
        )
        db.add(question)
        db.flush()  # Get the question ID

        # Create options (new format with key, text, is_correct, rationale)
        options_data = q_data.get("options", [])
        for option_data in options_data:
            if not isinstance(option_data, dict):
                continue

            key = option_data.get("key", "")
            text = option_data.get("text", "")
            is_correct = option_data.get("is_correct", False)
            rationale = option_data.get("rationale", "")

            if not key or not text:
                continue

            option = QuestionOption(
                question_id=question.question_id,
                key=key.upper(),
                text=text,
                is_correct=is_correct,
                rationale=rationale,
            )
            db.add(option)

        added += 1

    db.commit()
    return added


def seed_quizzes_for_sector(sector_name: str, force: bool = False) -> None:
    """
    Seed quizzes for a specific sector only.

    Args:
        sector_name: Name of the sector (e.g., 'education', 'technology')
        force: If True, will add even if quizzes exist
    """
    db = get_db_session()

    try:
        data = load_sector_file(sector_name)
        if not data:
            print(f"❌ Could not load {sector_name}.json")
            return

        quizzes_data = data.get("quizzes", [])
        if not quizzes_data:
            print(f"⚠️  No quizzes found in {sector_name}.json")
            return

        print(f"📝 Seeding {len(quizzes_data)} quiz(zes) for sector: {sector_name}")

        added_quizzes = 0
        added_questions = 0
        skipped_quizzes = 0

        for quiz_data in quizzes_data:
            spec_name = quiz_data.get("specialization", "")
            specialization = find_specialization(db, spec_name)

            if not specialization:
                print(f"   ⚠️  Specialization '{spec_name}' not found")
                skipped_quizzes += 1
                continue

            # Check if quiz already exists
            existing_quiz = (
                db.query(Quiz)
                .filter(
                    Quiz.title == quiz_data["title"],
                    Quiz.specialization_id == specialization.specialization_id,
                )
                .first()
            )

            if existing_quiz and not force:
                continue

            if existing_quiz and force:
                # Delete existing to replace
                db.delete(existing_quiz)
                db.commit()

            # Create quiz
            quiz = Quiz(
                title=quiz_data["title"],
                description=quiz_data.get("description", ""),
                specialization_id=specialization.specialization_id,
                difficulty_level=quiz_data.get("difficulty_level", 1),
                time_limit_minutes=quiz_data.get("time_limit_minutes", 30),
                passing_score=quiz_data.get("passing_score", 70.0),
            )
            db.add(quiz)
            db.commit()
            db.refresh(quiz)
            added_quizzes += 1

            # Create questions
            questions_added = _seed_quiz_questions(
                db, quiz.quiz_id, quiz_data.get("questions", [])
            )
            added_questions += questions_added

        print(f"✅ Seeding complete for {sector_name}!")
        print(f"   - Quizzes added: {added_quizzes}")
        print(f"   - Questions added: {added_questions}")
        if skipped_quizzes > 0:
            print(f"   - Skipped (missing specialization): {skipped_quizzes}")

    except Exception as e:
        print(f"❌ Error seeding quizzes: {e}")
        import traceback

        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    import sys

    force = "--force" in sys.argv

    # Check if a specific sector was requested
    sector_arg = None
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            sector_arg = arg
            break

    if sector_arg:
        seed_quizzes_for_sector(sector_arg, force=force)
    else:
        seed_quizzes(force=force)
