"""
Quiz API endpoints.

Updated for new question format (v2):
- Options have key (A-E), text, is_correct, rationale
- Users submit answers by key (A, B, C, D, E)
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from src.app.db.session import get_db
from src.app.modules.quizzes.service import QuizService
from src.app.modules.quizzes.schema import (
    QuizSubmission,
    QuizListResponse,
    QuizDetail,
    QuizStartResponse,
    QuizSubmitResponse,
    AttemptResultResponse,
    QuizSummary,
    QuestionInQuiz,
    OptionInQuiz,
    QuestionResult,
    OptionWithAnswer,
)
from src.app.modules.goals.service import GoalService
from src.app.modules.benchmarks.service import BenchmarkService
from src.app.modules.users.service import UserService
from src.app.modules.users.models import User
from src.app.modules.sectors.models import Specialization

router = APIRouter()


# ============================================================
# QUIZ ENDPOINTS
# ============================================================


@router.get("/", response_model=QuizListResponse)
def get_all_quizzes(
    specialization_id: Optional[UUID] = None, db: Session = Depends(get_db)
):
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
        quiz_list.append(
            QuizSummary(
                quiz_id=str(quiz.quiz_id),
                title=quiz.title,
                description=quiz.description,
                difficulty_level=quiz.difficulty_level,
                time_limit_minutes=quiz.time_limit_minutes,
                passing_score=quiz.passing_score,
                question_count=len(quiz.questions) if quiz.questions else 0,
                specialization_id=str(quiz.specialization_id),
                specialization_name=quiz.specialization.name if quiz.specialization else None,
            )
        )

    return {"quizzes": quiz_list, "total": len(quiz_list)}


@router.get("/by-specialization/{specialization_id}", response_model=QuizListResponse)
def get_quizzes_by_specialization(specialization_id: UUID, db: Session = Depends(get_db)):
    """Get all quizzes for a specific specialization."""
    quizzes = QuizService.get_quizzes_by_specialization(db, specialization_id)

    # Get specialization name
    specialization = (
        db.query(Specialization)
        .filter(Specialization.specialization_id == specialization_id)
        .first()
    )
    specialization_name = specialization.name if specialization else None

    quiz_list = []
    for quiz in quizzes:
        quiz_list.append(
            QuizSummary(
                quiz_id=str(quiz.quiz_id),
                title=quiz.title,
                description=quiz.description,
                difficulty_level=quiz.difficulty_level,
                time_limit_minutes=quiz.time_limit_minutes,
                passing_score=quiz.passing_score,
                question_count=len(quiz.questions) if quiz.questions else 0,
                specialization_id=str(quiz.specialization_id),
                specialization_name=specialization_name,
            )
        )

    return {"quizzes": quiz_list, "total": len(quiz_list)}


@router.get("/{quiz_id}", response_model=QuizDetail)
def get_quiz(quiz_id: UUID, db: Session = Depends(get_db)):
    """
    Get a quiz with all questions and options.
    Options are returned without revealing correct answers (for taking the quiz).
    """
    quiz = QuizService.get_quiz_by_id(db, quiz_id)

    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    questions = QuizService.get_quiz_questions(db, quiz_id)

    # Build question list with options (without revealing answers)
    question_list = []
    for question in questions:
        # Sort options by order_index
        sorted_options = sorted(question.options, key=lambda x: x.order_index)

        options = []
        for option in sorted_options:
            options.append(
                OptionInQuiz(
                    key=option.key,
                    text=option.text,
                )
            )

        question_list.append(
            QuestionInQuiz(
                question_id=str(question.question_id),
                question_text=question.question_text,
                question_type=question.question_type,
                points=question.points,
                order_index=question.order_index,
                options=options,
            )
        )

    return QuizDetail(
        quiz_id=str(quiz.quiz_id),
        title=quiz.title,
        description=quiz.description,
        difficulty_level=quiz.difficulty_level,
        time_limit_minutes=quiz.time_limit_minutes,
        passing_score=quiz.passing_score,
        question_count=len(questions),
        specialization_id=str(quiz.specialization_id),
        questions=question_list,
    )


@router.post("/{quiz_id}/start", response_model=QuizStartResponse)
def start_quiz(quiz_id: UUID, user_id: UUID, db: Session = Depends(get_db)):
    """Start a quiz attempt and return the quiz with questions."""
    quiz = QuizService.get_quiz_by_id(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    attempt = QuizService.create_quiz_attempt(db, user_id, quiz_id)

    # Get quiz detail for response
    questions = QuizService.get_quiz_questions(db, quiz_id)

    question_list = []
    for question in questions:
        sorted_options = sorted(question.options, key=lambda x: x.order_index)
        options = [
            OptionInQuiz(key=opt.key, text=opt.text) for opt in sorted_options
        ]
        question_list.append(
            QuestionInQuiz(
                question_id=str(question.question_id),
                question_text=question.question_text,
                question_type=question.question_type,
                points=question.points,
                order_index=question.order_index,
                options=options,
            )
        )

    quiz_detail = QuizDetail(
        quiz_id=str(quiz.quiz_id),
        title=quiz.title,
        description=quiz.description,
        difficulty_level=quiz.difficulty_level,
        time_limit_minutes=quiz.time_limit_minutes,
        passing_score=quiz.passing_score,
        question_count=len(questions),
        specialization_id=str(quiz.specialization_id),
        questions=question_list,
    )

    return QuizStartResponse(
        attempt_id=str(attempt.attempt_id),
        quiz_id=str(quiz_id),
        quiz=quiz_detail,
        message="Quiz started successfully",
    )


# ============================================================
# ATTEMPT ENDPOINTS
# ============================================================


@router.post("/attempts/{attempt_id}/submit", response_model=QuizSubmitResponse)
def submit_quiz(attempt_id: UUID, data: QuizSubmission, db: Session = Depends(get_db)):
    """
    Submit quiz answers and get results.

    Answers should contain:
    - question_id: UUID
    - selected_key: str (A, B, C, D, or E)
    """
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
                BenchmarkService.calculate_peer_benchmarks(
                    db, user.preferred_specialization_id
                )
                print(
                    f"Peer benchmarks updated for specialization {user.preferred_specialization_id}"
                )
            except Exception as e:
                print(f"Failed to update peer benchmarks: {e}")

    # Convert question_results to proper format
    question_results = []
    for qr in result.get("question_results", []):
        options = [
            OptionWithAnswer(
                key=opt["key"],
                text=opt["text"],
                is_correct=opt["is_correct"],
                rationale=opt.get("rationale"),
            )
            for opt in qr.get("options", [])
        ]
        question_results.append(
            QuestionResult(
                question_id=qr["question_id"],
                question_text=qr["question_text"],
                user_answer=qr["user_answer"],
                correct_answer=qr["correct_answer"],
                is_correct=qr["is_correct"],
                points=qr["points"],
                earned_points=qr["earned_points"],
                explanation=qr.get("explanation"),
                options=options,
            )
        )

    return QuizSubmitResponse(
        success=True,
        score=result["score"],
        max_score=result["max_score"],
        percentage=result["score"],  # score is already percentage
        correct_count=result["correct"],
        total_count=result["total"],
        passed=result["passed"],
        message=result.get("feedback", {}).get("overall", "Quiz completed!"),
        quiz_title=result.get("quiz_title", ""),
        passing_score=result.get("passing_score", 70.0),
        time_taken_minutes=result.get("time_taken_minutes"),
        readiness=readiness,
        feedback=result.get("feedback"),
        question_results=question_results,
        score_impact=result.get("score_impact"),
        updated_goals=updated_goals,
    )


@router.get("/attempts/{attempt_id}/results", response_model=AttemptResultResponse)
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

    # Get questions with answers for review
    questions = QuizService.get_quiz_questions(db, quiz.quiz_id)
    question_results = []

    for question in questions:
        sorted_options = sorted(question.options, key=lambda x: x.order_index)
        correct_key = None

        options = []
        for opt in sorted_options:
            if opt.is_correct:
                correct_key = opt.key
            options.append(
                OptionWithAnswer(
                    key=opt.key,
                    text=opt.text,
                    is_correct=opt.is_correct,
                    rationale=opt.rationale,
                )
            )

        question_results.append(
            QuestionResult(
                question_id=str(question.question_id),
                question_text=question.question_text,
                user_answer="",  # Not stored in attempt, would need to track separately
                correct_answer=correct_key or "",
                is_correct=False,  # Can't determine without stored answers
                points=question.points,
                earned_points=0,
                explanation=question.explanation,
                options=options,
            )
        )

    return AttemptResultResponse(
        attempt={
            "attempt_id": str(attempt.attempt_id),
            "quiz_id": str(attempt.quiz_id),
            "score": attempt.score,
            "percentage": attempt.percentage,
            "passed": attempt.is_passed,
            "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None,
        },
        quiz={
            "quiz_id": str(quiz.quiz_id),
            "title": quiz.title,
            "description": quiz.description,
            "difficulty_level": quiz.difficulty_level,
            "passing_score": quiz.passing_score,
        },
        question_results=question_results,
        readiness=readiness,
    )
