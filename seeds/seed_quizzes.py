"""
Seed quizzes and questions.
Loads data from data/quizzes.json
"""

from typing import List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session

from seeds.base import load_json_file, get_db_session
from src.app.modules.sectors.models import Specialization
from src.app.modules.quizzes.models import Quiz, Question, QuestionOption


def seed_quizzes(force: bool = False) -> None:
    """
    Seed quizzes and questions from JSON.

    Args:
        force: If True, will add missing quizzes even if some exist
    """
    db = get_db_session()

    try:
        # Check if quizzes already exist
        existing_count = db.query(Quiz).count()

        if existing_count > 0 and not force:
            print(f"✅ Quizzes already seeded: {existing_count} quiz(zes) found")
            return

        # Load quizzes from JSON
        data = load_json_file("quizzes.json")
        if not data:
            print("❌ Could not load quizzes.json")
            return

        quizzes_data = data.get("quizzes", [])
        if not quizzes_data:
            print("⚠️  No quizzes found in quizzes.json")
            return

        print(f"📝 Seeding {len(quizzes_data)} quiz(zes)...")

        added_quizzes = 0
        added_questions = 0
        skipped_quizzes = 0

        for quiz_data in quizzes_data:
            # Find specialization by name
            specialization = (
                db.query(Specialization).filter(Specialization.name == quiz_data["specialization"]).first()
            )

            if not specialization:
                print(
                    f"  ⚠️  Specialization '{quiz_data['specialization']}' not found, skipping quiz: {quiz_data['title']}"
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
                print(f"  ⏩ Quiz '{quiz_data['title']}' already exists")
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
            print(f"  ✅ Created quiz: {quiz.title}")

            # Create questions
            questions_added = _seed_quiz_questions(db, quiz.quiz_id, quiz_data.get("questions", []))
            added_questions += questions_added

        print(f"✅ Quiz seeding complete!")
        print(f"   - Quizzes added: {added_quizzes}")
        print(f"   - Questions added: {added_questions}")
        if skipped_quizzes > 0:
            print(f"   - Quizzes skipped (missing specialization): {skipped_quizzes}")

    except Exception as e:
        print(f"❌ Error seeding quizzes: {e}")
        import traceback

        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


def _seed_quiz_questions(db: Session, quiz_id: UUID, questions_data: List[Dict[str, Any]]) -> int:
    """
    Seed questions for a quiz.

    Returns:
        Number of questions added
    """
    added = 0

    for idx, q_data in enumerate(questions_data):
        question = Question(
            quiz_id=quiz_id,
            question_text=q_data["question_text"],
            question_type=q_data.get("question_type", "multiple_choice"),
            points=q_data.get("points", 1),
            order_index=idx + 1,
            explanation=q_data.get("explanation"),
        )
        db.add(question)
        db.flush()  # Get the question ID

        # Create options
        for opt_idx, option_data in enumerate(q_data.get("options", [])):
            option = QuestionOption(
                question_id=question.question_id,
                option_text=option_data["text"],
                is_correct=option_data.get("is_correct", False),
                order_index=opt_idx + 1,
            )
            db.add(option)

        added += 1

    db.commit()
    return added


def seed_expanded_quizzes() -> None:
    """
    Seed additional quizzes from expanded_quizzes.json.
    This can be called separately to add more quiz content.
    """
    db = get_db_session()

    try:
        data = load_json_file("expanded_quizzes.json")
        if not data:
            print("❌ Could not load expanded_quizzes.json")
            return

        quizzes_data = data.get("quizzes", [])
        print(f"📝 Seeding {len(quizzes_data)} expanded quiz(zes)...")

        added_quizzes = 0

        for quiz_data in quizzes_data:
            specialization = (
                db.query(Specialization).filter(Specialization.name == quiz_data["specialization"]).first()
            )

            if not specialization:
                continue

            existing_quiz = (
                db.query(Quiz)
                .filter(
                    Quiz.title == quiz_data["title"],
                    Quiz.specialization_id == specialization.specialization_id,
                )
                .first()
            )

            if existing_quiz:
                continue

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

            _seed_quiz_questions(db, quiz.quiz_id, quiz_data.get("questions", []))
            added_quizzes += 1

        print(f"✅ Expanded quiz seeding complete! Added {added_quizzes} quiz(zes)")

    except Exception as e:
        print(f"❌ Error seeding expanded quizzes: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_quizzes(force=False)

