"""
Goal service - handles goal and journal entry business logic.
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from src.app.modules.goals.models import Goal, JournalEntry
from src.app.modules.users.models import User


class GoalService:
    """Service class for goal-related operations."""

    # ============================================================
    # GOAL OPERATIONS
    # ============================================================

    @staticmethod
    def create_goal(
        db: Session,
        user_id: UUID,
        title: str,
        description: str,
        category: str,
        target_value: float,
        target_date: Optional[datetime] = None,
    ) -> Goal:
        """Create a new goal for a user."""
        goal = Goal(
            user_id=user_id,
            title=title,
            description=description,
            category=category,
            target_value=target_value,
            current_value=0.0,
            is_completed=False,
            target_date=target_date,
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
        return goal

    @staticmethod
    def get_user_goals(db: Session, user_id: UUID) -> List[Goal]:
        """Get all goals for a user."""
        return db.query(Goal).filter(Goal.user_id == user_id).order_by(Goal.created_at.desc()).all()

    @staticmethod
    def get_goal_by_id(db: Session, goal_id: UUID, user_id: UUID) -> Optional[Goal]:
        """Get a specific goal by ID for a user."""
        return db.query(Goal).filter(Goal.goal_id == goal_id, Goal.user_id == user_id).first()

    @staticmethod
    def update_goal(db: Session, goal_id: UUID, user_id: UUID, **kwargs) -> Optional[Goal]:
        """Update a goal."""
        goal = db.query(Goal).filter(Goal.goal_id == goal_id, Goal.user_id == user_id).first()
        if not goal:
            return None

        for key, value in kwargs.items():
            if hasattr(goal, key) and value is not None:
                setattr(goal, key, value)

        db.commit()
        db.refresh(goal)
        return goal

    @staticmethod
    def update_goal_progress(db: Session, goal_id: UUID, user_id: UUID, current_value: float) -> Optional[Goal]:
        """Update goal progress and auto-complete if target reached."""
        goal = db.query(Goal).filter(Goal.goal_id == goal_id, Goal.user_id == user_id).first()
        if not goal:
            return None

        goal.current_value = current_value

        # Auto-complete if target reached
        if goal.current_value >= goal.target_value:
            goal.is_completed = True

        db.commit()
        db.refresh(goal)
        return goal

    @staticmethod
    def delete_goal(db: Session, goal_id: UUID, user_id: UUID) -> bool:
        """Delete a goal."""
        goal = db.query(Goal).filter(Goal.goal_id == goal_id, Goal.user_id == user_id).first()
        if not goal:
            return False

        db.delete(goal)
        db.commit()
        return True

    @staticmethod
    def auto_update_goals_on_quiz_completion(db: Session, user_id: UUID) -> List[Dict[str, Any]]:
        """
        Automatically update user goals based on their current readiness scores.
        Called after quiz completion to sync goals with actual progress.
        """
        try:
            # Get current user
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                return []

            # Get all active (not completed) goals for this user
            active_goals = db.query(Goal).filter(Goal.user_id == user_id, Goal.is_completed == False).all()

            updated_goals = []

            for goal in active_goals:
                # Map goal category to user score field
                score_mapping = {
                    "readiness": user.readiness_score,
                    "technical": user.technical_score,
                    "soft_skills": user.soft_skills_score,
                    "leadership": user.leadership_score,
                }

                # Get the corresponding score for this goal category
                current_score = score_mapping.get(goal.category)

                if current_score is not None:
                    old_value = goal.current_value
                    goal.current_value = current_score

                    # Check if goal is now completed
                    if goal.current_value >= goal.target_value and not goal.is_completed:
                        goal.is_completed = True
                        updated_goals.append({
                            "goal_id": str(goal.goal_id),
                            "title": goal.title,
                            "category": goal.category,
                            "completed": True,
                            "progress": goal.current_value,
                        })
                    elif old_value != current_score:
                        updated_goals.append({
                            "goal_id": str(goal.goal_id),
                            "title": goal.title,
                            "category": goal.category,
                            "completed": False,
                            "progress": goal.current_value,
                        })

            db.commit()
            return updated_goals

        except Exception as e:
            print(f"Error auto-updating goals: {e}")
            db.rollback()
            return []

    # ============================================================
    # JOURNAL ENTRY OPERATIONS
    # ============================================================

    @staticmethod
    def create_journal_entry(
        db: Session,
        user_id: UUID,
        content: str,
        prompt: Optional[str] = None,
    ) -> JournalEntry:
        """Create a new journal entry."""
        entry = JournalEntry(
            user_id=user_id,
            content=content,
            prompt=prompt,
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def get_user_journal_entries(db: Session, user_id: UUID, limit: int = 20) -> List[JournalEntry]:
        """Get journal entries for a user."""
        return (
            db.query(JournalEntry)
            .filter(JournalEntry.user_id == user_id)
            .order_by(JournalEntry.entry_date.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_journal_entry_by_id(db: Session, entry_id: UUID, user_id: UUID) -> Optional[JournalEntry]:
        """Get a specific journal entry by ID for a user."""
        return (
            db.query(JournalEntry).filter(JournalEntry.entry_id == entry_id, JournalEntry.user_id == user_id).first()
        )

    @staticmethod
    def update_journal_entry(db: Session, entry_id: UUID, user_id: UUID, content: str) -> Optional[JournalEntry]:
        """Update a journal entry."""
        entry = (
            db.query(JournalEntry).filter(JournalEntry.entry_id == entry_id, JournalEntry.user_id == user_id).first()
        )
        if not entry:
            return None

        entry.content = content
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def delete_journal_entry(db: Session, entry_id: UUID, user_id: UUID) -> bool:
        """Delete a journal entry."""
        entry = (
            db.query(JournalEntry).filter(JournalEntry.entry_id == entry_id, JournalEntry.user_id == user_id).first()
        )
        if not entry:
            return False

        db.delete(entry)
        db.commit()
        return True

