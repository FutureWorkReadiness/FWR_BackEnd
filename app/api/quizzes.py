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

@router.get("/quizzes/{quiz_id}", response_model=schemas.Quiz)
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    quiz = crud.get_quiz_by_id(db, quiz_id)
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    questions = crud.get_quiz_questions(db, quiz_id)
    
    quiz_data = {
        "id": quiz.id,
        "title": quiz.title,
        "description": quiz.description,
        "duration": quiz.time_limit_minutes,
        "question_count": len(questions),
        "difficulty": quiz.difficulty_level,
        "questions": []
    }
    
    for question in questions:
        quiz_data["questions"].append({
            "id": question.id,
            "question": question.question_text,
            "options": [option.option_text for option in question.options]
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

@router.post("/attempts/{attempt_id}/submit", response_model=schemas.QuizResult)
def submit_quiz(attempt_id: int, data: schemas.QuizSubmission, db: Session = Depends(get_db)):
    answers = [{"question_id": a.question_id, "selected_answer": a.selected_answer} 
               for a in data.answers]
    
    result = crud.submit_quiz_attempt(db, attempt_id, answers)
    
    if not result:
        raise HTTPException(status_code=404, detail="Attempt not found")
    
    return {
        "success": True,
        "score": result["score"],
        "correct": result["correct"],
        "total": result["total"],
        "passed": result["passed"],
        "message": "Great job!" if result["passed"] else "Keep practicing!"
    }

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