from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas
from ..database import get_db

router = APIRouter()

@router.post("/goals", response_model=schemas.Goal)
def create_goal(goal: schemas.GoalCreate, user_id: int = Query(...), db: Session = Depends(get_db)):
    """Create a new goal for a user"""
    db_goal = crud.create_goal(
        db=db,
        user_id=user_id,
        title=goal.title,
        description=goal.description,
        category=goal.category,
        target_value=goal.target_value,
        target_date=goal.target_date
    )
    return db_goal

@router.get("/goals", response_model=List[schemas.Goal])
def get_goals(user_id: int = Query(...), db: Session = Depends(get_db)):
    """Get all goals for a user"""
    goals = crud.get_user_goals(db, user_id)
    return goals

@router.put("/goals/{goal_id}", response_model=schemas.Goal)
def update_goal(goal_id: int, goal_update: schemas.GoalCreate, user_id: int = Query(...), db: Session = Depends(get_db)):
    """Update a goal"""
    updated_goal = crud.update_goal(
        db=db,
        goal_id=goal_id,
        user_id=user_id,
        title=goal_update.title,
        description=goal_update.description,
        category=goal_update.category,
        target_value=goal_update.target_value,
        target_date=goal_update.target_date
    )
    if not updated_goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return updated_goal

@router.patch("/goals/{goal_id}/progress")
def update_goal_progress(goal_id: int, current_value: float = Query(...), user_id: int = Query(...), db: Session = Depends(get_db)):
    """Update goal progress (current_value)"""
    goal = crud.update_goal(db=db, goal_id=goal_id, user_id=user_id, current_value=current_value)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    # Auto-complete if target reached
    if goal.current_value >= goal.target_value:
        crud.update_goal(db=db, goal_id=goal_id, user_id=user_id, is_completed=True)
        goal.is_completed = True
    return goal

@router.delete("/goals/{goal_id}")
def delete_goal(goal_id: int, user_id: int = Query(...), db: Session = Depends(get_db)):
    """Delete a goal"""
    success = crud.delete_goal(db, goal_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"success": True, "message": "Goal deleted"}

# Journal Entry endpoints
@router.post("/journal", response_model=schemas.JournalEntry)
def create_journal_entry(entry: schemas.JournalEntryCreate, user_id: int = Query(...), db: Session = Depends(get_db)):
    """Create a new journal entry"""
    db_entry = crud.create_journal_entry(
        db=db,
        user_id=user_id,
        content=entry.content,
        prompt=entry.prompt
    )
    return db_entry

@router.get("/journal", response_model=List[schemas.JournalEntry])
def get_journal_entries(user_id: int = Query(...), limit: int = Query(20), db: Session = Depends(get_db)):
    """Get journal entries for a user"""
    entries = crud.get_user_journal_entries(db, user_id, limit)
    return entries

@router.put("/journal/{entry_id}", response_model=schemas.JournalEntry)
def update_journal_entry(entry_id: int, entry_update: schemas.JournalEntryUpdate, user_id: int = Query(...), db: Session = Depends(get_db)):
    """Update a journal entry"""
    updated_entry = crud.update_journal_entry(db, entry_id, user_id, entry_update.content)
    if not updated_entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return updated_entry

@router.delete("/journal/{entry_id}")
def delete_journal_entry(entry_id: int, user_id: int = Query(...), db: Session = Depends(get_db)):
    """Delete a journal entry"""
    success = crud.delete_journal_entry(db, entry_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return {"success": True, "message": "Journal entry deleted"}

