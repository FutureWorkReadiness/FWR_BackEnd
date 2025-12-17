"""
Goal and Journal Entry API endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID

from src.app.db.session import get_db
from src.app.modules.goals.service import GoalService
from src.app.modules.goals.schema import GoalCreate, JournalEntryCreate, JournalEntryUpdate

router = APIRouter()


# ============================================================
# GOAL ENDPOINTS
# ============================================================


@router.post("/")
def create_goal(goal: GoalCreate, user_id: UUID = Query(...), db: Session = Depends(get_db)):
    """Create a new goal for a user."""
    db_goal = GoalService.create_goal(
        db=db,
        user_id=user_id,
        title=goal.title,
        description=goal.description,
        category=goal.category,
        target_value=goal.target_value,
        target_date=goal.target_date,
    )
    return {
        "goal_id": str(db_goal.goal_id),
        "user_id": str(db_goal.user_id),
        "title": db_goal.title,
        "description": db_goal.description,
        "category": db_goal.category,
        "target_value": db_goal.target_value,
        "current_value": db_goal.current_value,
        "is_completed": db_goal.is_completed,
        "target_date": db_goal.target_date.isoformat() if db_goal.target_date else None,
        "created_at": db_goal.created_at.isoformat() if db_goal.created_at else None,
        "updated_at": db_goal.updated_at.isoformat() if db_goal.updated_at else None,
    }


@router.get("/")
def get_goals(user_id: UUID = Query(...), db: Session = Depends(get_db)):
    """Get all goals for a user."""
    goals = GoalService.get_user_goals(db, user_id)
    return [
        {
            "goal_id": str(goal.goal_id),
            "user_id": str(goal.user_id),
            "title": goal.title,
            "description": goal.description,
            "category": goal.category,
            "target_value": goal.target_value,
            "current_value": goal.current_value,
            "is_completed": goal.is_completed,
            "target_date": goal.target_date.isoformat() if goal.target_date else None,
            "created_at": goal.created_at.isoformat() if goal.created_at else None,
            "updated_at": goal.updated_at.isoformat() if goal.updated_at else None,
        }
        for goal in goals
    ]


@router.put("/{goal_id}")
def update_goal(
    goal_id: UUID,
    goal_update: GoalCreate,
    user_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    """Update a goal."""
    updated_goal = GoalService.update_goal(
        db=db,
        goal_id=goal_id,
        user_id=user_id,
        title=goal_update.title,
        description=goal_update.description,
        category=goal_update.category,
        target_value=goal_update.target_value,
        target_date=goal_update.target_date,
    )
    if not updated_goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return {
        "goal_id": str(updated_goal.goal_id),
        "user_id": str(updated_goal.user_id),
        "title": updated_goal.title,
        "description": updated_goal.description,
        "category": updated_goal.category,
        "target_value": updated_goal.target_value,
        "current_value": updated_goal.current_value,
        "is_completed": updated_goal.is_completed,
        "target_date": updated_goal.target_date.isoformat() if updated_goal.target_date else None,
        "created_at": updated_goal.created_at.isoformat() if updated_goal.created_at else None,
        "updated_at": updated_goal.updated_at.isoformat() if updated_goal.updated_at else None,
    }


@router.patch("/{goal_id}/progress")
def update_goal_progress(
    goal_id: UUID,
    current_value: float = Query(...),
    user_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    """Update goal progress (current_value)."""
    goal = GoalService.update_goal_progress(db=db, goal_id=goal_id, user_id=user_id, current_value=current_value)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return {
        "goal_id": str(goal.goal_id),
        "user_id": str(goal.user_id),
        "title": goal.title,
        "current_value": goal.current_value,
        "target_value": goal.target_value,
        "is_completed": goal.is_completed,
    }


@router.delete("/{goal_id}")
def delete_goal(goal_id: UUID, user_id: UUID = Query(...), db: Session = Depends(get_db)):
    """Delete a goal."""
    success = GoalService.delete_goal(db, goal_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"success": True, "message": "Goal deleted"}


# ============================================================
# JOURNAL ENTRY ENDPOINTS
# ============================================================


@router.post("/journal")
def create_journal_entry(
    entry: JournalEntryCreate,
    user_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    """Create a new journal entry."""
    db_entry = GoalService.create_journal_entry(db=db, user_id=user_id, content=entry.content, prompt=entry.prompt)
    return {
        "entry_id": str(db_entry.entry_id),
        "user_id": str(db_entry.user_id),
        "content": db_entry.content,
        "prompt": db_entry.prompt,
        "entry_date": db_entry.entry_date.isoformat() if db_entry.entry_date else None,
        "created_at": db_entry.created_at.isoformat() if db_entry.created_at else None,
        "updated_at": db_entry.updated_at.isoformat() if db_entry.updated_at else None,
    }


@router.get("/journal")
def get_journal_entries(user_id: UUID = Query(...), limit: int = Query(20), db: Session = Depends(get_db)):
    """Get journal entries for a user."""
    entries = GoalService.get_user_journal_entries(db, user_id, limit)
    return [
        {
            "entry_id": str(entry.entry_id),
            "user_id": str(entry.user_id),
            "content": entry.content,
            "prompt": entry.prompt,
            "entry_date": entry.entry_date.isoformat() if entry.entry_date else None,
            "created_at": entry.created_at.isoformat() if entry.created_at else None,
            "updated_at": entry.updated_at.isoformat() if entry.updated_at else None,
        }
        for entry in entries
    ]


@router.put("/journal/{entry_id}")
def update_journal_entry(
    entry_id: UUID,
    entry_update: JournalEntryUpdate,
    user_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    """Update a journal entry."""
    updated_entry = GoalService.update_journal_entry(db, entry_id, user_id, entry_update.content)
    if not updated_entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return {
        "entry_id": str(updated_entry.entry_id),
        "user_id": str(updated_entry.user_id),
        "content": updated_entry.content,
        "prompt": updated_entry.prompt,
        "entry_date": updated_entry.entry_date.isoformat() if updated_entry.entry_date else None,
        "created_at": updated_entry.created_at.isoformat() if updated_entry.created_at else None,
        "updated_at": updated_entry.updated_at.isoformat() if updated_entry.updated_at else None,
    }


@router.delete("/journal/{entry_id}")
def delete_journal_entry(entry_id: UUID, user_id: UUID = Query(...), db: Session = Depends(get_db)):
    """Delete a journal entry."""
    success = GoalService.delete_journal_entry(db, entry_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return {"success": True, "message": "Journal entry deleted"}

