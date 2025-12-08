"""
API endpoints for handling user feedback
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db

router = APIRouter()

@router.post("/feedback/", response_model=schemas.Feedback)
def create_feedback(
    feedback: schemas.FeedbackCreate,
    db: Session = Depends(get_db)
):
    """
    Submit new feedback.
    - **rating**: Optional integer rating (e.g., 1-5).
    - **feedback_text**: Optional feedback message.
    - **user_id**: Optional user ID if feedback is not anonymous.
    - **quiz_id**: Optional quiz ID to associate feedback with a quiz.
    """
    return crud.create_feedback(db=db, feedback=feedback)
