from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from .. import crud, schemas
from .. import models_hierarchical as models
from ..database import get_db

router = APIRouter()

# We now use schemas from schemas.py instead of defining models here

# ENDPOINTS
@router.get("/quizzes", response_model=schemas.QuizzesResponse)
def get_all_quizzes(db: Session = Depends(get_db)):
    quizzes = crud.get_all_quizzes(db)
    
    quiz_list = []
    for quiz in quizzes:
        quiz_list.append({
            "id": quiz.id,
            "title": quiz.title,
            "description": quiz.description,
            "specialization_id": quiz.specialization_id,
            "specialization_name": quiz.specialization.name if quiz.specialization else None,
            "duration": quiz.time_limit_minutes,
            "question_count": len(quiz.questions) if quiz.questions else 0,
            "difficulty": quiz.difficulty_level
        })
    
    return {"quizzes": quiz_list}

@router.get("/quizzes/{quiz_id}")
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    """Get a quiz with all questions and options - returns custom format"""
    quiz = crud.get_quiz_by_id(db, quiz_id)
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    questions = crud.get_quiz_questions(db, quiz_id)
    
    # Build response matching frontend expectations
    quiz_data = {
        "id": quiz.id,
        "title": quiz.title,
        "description": quiz.description,
        "duration": quiz.time_limit_minutes,
        "question_count": len(questions),
        "difficulty": quiz.difficulty_level,
        "specialization_id": quiz.specialization_id,
        "questions": []
    }
    
    for question in questions:
        # Get all options with their correct status
        options = []
        correct_index = None
        for idx, option in enumerate(question.options):
            options.append({
                "text": option.option_text,
                "is_correct": option.is_correct
            })
            if option.is_correct:
                correct_index = idx
        
        quiz_data["questions"].append({
            "id": question.id,
            "question": question.question_text,
            "options": options,
            "correct_index": correct_index,
            "explanation": question.explanation
        })
    
    return quiz_data

@router.post("/quizzes/{quiz_id}/start", response_model=schemas.QuizStartResponse)
def start_quiz(quiz_id: int, user_id: int, db: Session = Depends(get_db)):
    quiz = crud.get_quiz_by_id(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    attempt = crud.create_quiz_attempt(db, user_id, quiz_id)
    
    return {
        "attempt_id": attempt.id,
        "quiz_id": quiz_id,
        "message": "Quiz started successfully"
    }

@router.post("/attempts/{attempt_id}/submit", response_model=schemas.QuizResultExtended)
def submit_quiz(attempt_id: int, data: schemas.QuizSubmission, db: Session = Depends(get_db)):
    # Use the superior submit_quiz_answers function with proper typing
    result = crud.submit_quiz_answers(db, attempt_id, data.answers)
    
    if not result:
        raise HTTPException(status_code=404, detail="Attempt not found")
    
    # Recompute readiness for the attempt's user
    attempt = crud.get_quiz_attempt(db, attempt_id)
    readiness = crud.recompute_user_readiness(db, attempt.user_id) if attempt else {"overall": 0.0, "technical": 0.0, "soft": 0.0}
    
    # Return all the detailed data from submit_quiz_answers
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
    }

@router.get("/results/{attempt_id}")
def get_attempt_result(attempt_id: int, db: Session = Depends(get_db)):
    data = crud.get_attempt_with_quiz(db, attempt_id)
    if not data:
        raise HTTPException(status_code=404, detail="Attempt not found")
    attempt = data["attempt"]
    quiz = data["quiz"]
    readiness = crud.recompute_user_readiness(db, attempt.user_id) or {"overall": 0.0, "technical": 0.0, "soft": 0.0}
    return {
        "attempt": {
            "id": attempt.id,
            "quiz_id": attempt.quiz_id,
            "score": attempt.percentage,
            "passed": attempt.is_passed,
            "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None,
        },
        "quiz": {
            "id": quiz.id,
            "title": quiz.title,
            "description": quiz.description,
        },
        "readiness": readiness,
    }

@router.get("/dashboard", response_model=schemas.DashboardResponse)
def get_dashboard(user_id: int, db: Session = Depends(get_db)):
    summary = crud.get_dashboard_summary(db, user_id)
    if not summary:
        raise HTTPException(status_code=404, detail="User not found")
    return summary

@router.get("/specializations/{specialization_id}/quizzes", response_model=schemas.QuizzesResponse)
def get_quizzes_by_specialization(specialization_id: int, db: Session = Depends(get_db)):
    quizzes = crud.get_quizzes_by_specialization(db, specialization_id)
    
    return {
        "quizzes": [
            {
                "id": quiz.id,
                "title": quiz.title,
                "description": quiz.description,
                "duration": quiz.time_limit_minutes,
                "difficulty": quiz.difficulty_level,
                "question_count": len(quiz.questions) if quiz.questions else 0
            } for quiz in quizzes
        ]
    }