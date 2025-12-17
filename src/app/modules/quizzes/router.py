"""
Quiz API endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from src.app.db.session import get_db
from src.app.modules.quizzes.service import QuizService
from src.app.modules.quizzes.schema import QuizSubmission
from src.app.modules.goals.service import GoalService
from src.app.modules.benchmarks.service import BenchmarkService
from src.app.modules.users.service import UserService
from src.app.modules.users.models import User
from src.app.modules.sectors.models import Specialization

router = APIRouter()


# ============================================================
# QUIZ ENDPOINTS
# ============================================================


@router.get("/")
def get_all_quizzes(specialization_id: Optional[UUID] = None, db: Session = Depends(get_db)):
    """
    Get all quizzes, optionally filtered by specialization_id.
    If specialization_id is provided, only return quizzes for that specialization.
    """
    quizzes = QuizService.get_all_quizzes(db)

    # Filter by specialization if provided
    if specialization_id:
        quizzes = [q for q in quizzes if q.specialization_id == specialization_id]

    quiz_list = []
    for quiz in quizzes:
        quiz_list.append({
            "quiz_id": str(quiz.quiz_id),
            "title": quiz.title,
            "description": quiz.description,
            "specialization_id": str(quiz.specialization_id),
            "specialization_name": quiz.specialization.name if quiz.specialization else None,
            "duration": quiz.time_limit_minutes,
            "question_count": len(quiz.questions) if quiz.questions else 0,
            "difficulty": quiz.difficulty_level,
        })

    return {"quizzes": quiz_list}


@router.get("/by-specialization/{specialization_id}")
def get_quizzes_by_specialization(specialization_id: UUID, db: Session = Depends(get_db)):
    """Get all quizzes for a specific specialization."""
    quizzes = QuizService.get_quizzes_by_specialization(db, specialization_id)

    # Get specialization name
    specialization = (
        db.query(Specialization).filter(Specialization.specialization_id == specialization_id).first()
    )
    specialization_name = specialization.name if specialization else None

    return {
        "quizzes": [
            {
                "quiz_id": str(quiz.quiz_id),
                "title": quiz.title,
                "description": quiz.description,
                "duration": quiz.time_limit_minutes,
                "difficulty": quiz.difficulty_level,
                "question_count": len(quiz.questions) if quiz.questions else 0,
                "specialization_id": str(quiz.specialization_id),
                "specialization_name": specialization_name,
            }
            for quiz in quizzes
        ]
    }


@router.get("/{quiz_id}")
def get_quiz(quiz_id: UUID, db: Session = Depends(get_db)):
    """Get a quiz with all questions and options."""
    quiz = QuizService.get_quiz_by_id(db, quiz_id)

    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    questions = QuizService.get_quiz_questions(db, quiz_id)

    # Build response matching frontend expectations
    quiz_data = {
        "quiz_id": str(quiz.quiz_id),
        "title": quiz.title,
        "description": quiz.description,
        "duration": quiz.time_limit_minutes,
        "question_count": len(questions),
        "difficulty": quiz.difficulty_level,
        "specialization_id": str(quiz.specialization_id),
        "questions": [],
    }

    for question in questions:
        options = []
        correct_index = None
        for idx, option in enumerate(question.options):
            options.append({"text": option.option_text, "is_correct": option.is_correct})
            if option.is_correct:
                correct_index = idx

        quiz_data["questions"].append({
            "question_id": str(question.question_id),
            "question": question.question_text,
            "options": options,
            "correct_index": correct_index,
            "explanation": question.explanation,
        })

    return quiz_data


@router.post("/{quiz_id}/start")
def start_quiz(quiz_id: UUID, user_id: UUID, db: Session = Depends(get_db)):
    """Start a quiz attempt."""
    quiz = QuizService.get_quiz_by_id(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    attempt = QuizService.create_quiz_attempt(db, user_id, quiz_id)

    return {
        "attempt_id": str(attempt.attempt_id),
        "quiz_id": str(quiz_id),
        "message": "Quiz started successfully",
    }


# ============================================================
# ATTEMPT ENDPOINTS
# ============================================================


@router.post("/attempts/{attempt_id}/submit")
def submit_quiz(attempt_id: UUID, data: QuizSubmission, db: Session = Depends(get_db)):
    """Submit quiz answers and get results."""
    result = QuizService.submit_quiz_answers(db, attempt_id, data.answers)

    if not result:
        raise HTTPException(status_code=404, detail="Attempt not found")

    # Recompute readiness for the attempt's user
    attempt = QuizService.get_quiz_attempt(db, attempt_id)
    readiness = (
        QuizService.recompute_user_readiness(db, attempt.user_id)
        if attempt
        else {"overall": 0.0, "technical": 0.0, "soft": 0.0}
    )

    # Auto-update goals based on new readiness scores
    updated_goals = []
    if attempt:
        updated_goals = GoalService.auto_update_goals_on_quiz_completion(db, attempt.user_id)
        if updated_goals:
            print(f"Auto-updated {len(updated_goals)} goals for user {attempt.user_id}")

    # Update peer benchmarks for the user's specialization
    if attempt:
        user = db.query(User).filter(User.user_id == attempt.user_id).first()
        if user and user.preferred_specialization_id:
            try:
                BenchmarkService.calculate_peer_benchmarks(db, user.preferred_specialization_id)
                print(f"Peer benchmarks updated for specialization {user.preferred_specialization_id}")
            except Exception as e:
                print(f"Failed to update peer benchmarks: {e}")

    return {
        "success": True,
        "score": result["score"],
        "correct": result["correct"],
        "total": result["total"],
        "passed": result["passed"],
        "message": result.get("feedback", {}).get("overall", "Quiz completed!"),
        "readiness": readiness,
        "feedback": result.get("feedback"),
        "question_results": result.get("question_results"),
        "score_impact": result.get("score_impact"),
        "quiz_title": result.get("quiz_title"),
        "passing_score": result.get("passing_score"),
        "raw_score": result.get("raw_score"),
        "max_score": result.get("max_score"),
        "updated_goals": updated_goals,
    }


@router.get("/attempts/{attempt_id}/results")
def get_attempt_result(attempt_id: UUID, db: Session = Depends(get_db)):
    """Get results for a specific quiz attempt."""
    data = QuizService.get_attempt_with_quiz(db, attempt_id)
    if not data:
        raise HTTPException(status_code=404, detail="Attempt not found")

    attempt = data["attempt"]
    quiz = data["quiz"]
    readiness = QuizService.recompute_user_readiness(db, attempt.user_id) or {
        "overall": 0.0,
        "technical": 0.0,
        "soft": 0.0,
    }

    return {
        "attempt": {
            "attempt_id": str(attempt.attempt_id),
            "quiz_id": str(attempt.quiz_id),
            "score": attempt.percentage,
            "passed": attempt.is_passed,
            "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None,
        },
        "quiz": {
            "quiz_id": str(quiz.quiz_id),
            "title": quiz.title,
            "description": quiz.description,
        },
        "readiness": readiness,
    }

