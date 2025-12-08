"""
CRUD operations for database
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from . import schemas
from .models import models_hierarchical as models


def create_user(db: Session, email: str, password: str, name: str):
    """Create a new user"""
    db_user = models.User(
        email=email,
        password_hash=password,  # In production, this should be hashed
        name=name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    """Get user by email"""
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    """Get user by ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()

def update_user_specialization(db: Session, user_id: int, specialization_id: int):
    """Update user's specialization"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.preferred_specialization_id = specialization_id
        db.commit()
        db.refresh(user)
    return user

# SECTOR AND SPECIALIZATION OPERATIONS
def get_all_sectors(db: Session):
    """Get all sectors"""
    return db.query(models.Sector).all()

def get_specializations_by_sector(db: Session, sector_id: int):
    """Get all specializations for a sector (through branches)"""
    # Get all branches for this sector first, then get their specializations
    branches = get_branches_by_sector(db, sector_id)
    branch_ids = [branch.id for branch in branches]
    if not branch_ids:
        return []
    return db.query(models.Specialization).filter(
        models.Specialization.branch_id.in_(branch_ids)
    ).all()

def get_branches_by_sector(db: Session, sector_id: int):
    """Get all branches for a sector"""
    return db.query(models.Branch).filter(
        models.Branch.sector_id == sector_id
    ).all()

def get_specializations_by_branch(db: Session, branch_id: int):
    """Get all specializations for a branch"""
    return db.query(models.Specialization).filter(
        models.Specialization.branch_id == branch_id
    ).all()

def get_specialization_by_name(db: Session, name: str):
    """Get specialization by name"""
    return db.query(models.Specialization).filter(
        models.Specialization.name == name
    ).first()

# QUIZ OPERATIONS
def get_all_quizzes(db: Session):
    """Get all quizzes with their specializations"""
    return db.query(models.Quiz).join(models.Specialization).all()

def get_quiz_by_id(db: Session, quiz_id: int):
    """Get quiz by ID with questions and answer options"""
    return db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()

def get_quizzes_by_specialization(db: Session, specialization_id: int):
    """Get all quizzes for a specialization"""
    return db.query(models.Quiz).filter(
        models.Quiz.specialization_id == specialization_id
    ).all()

def get_quiz_questions(db: Session, quiz_id: int):
    """Get all questions for a quiz with their answer options"""
    return db.query(models.Question).filter(
        models.Question.quiz_id == quiz_id
    ).order_by(models.Question.order_index).all()

# QUIZ ATTEMPT OPERATIONS
def create_quiz_attempt(db: Session, user_id: int, quiz_id: int):
    """Create a new quiz attempt"""
    db_attempt = models.QuizAttempt(
        user_id=user_id,
        quiz_id=quiz_id,
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),  # Will be updated on submission
        score=0.0,
        max_score=0.0,
        percentage=0.0,
        is_passed=False
    )
    db.add(db_attempt)
    db.commit()
    db.refresh(db_attempt)
    return db_attempt

def get_quiz_attempt(db: Session, attempt_id: int):
    """Get quiz attempt by ID"""
    return db.query(models.QuizAttempt).filter(
        models.QuizAttempt.id == attempt_id
    ).first()

def get_user_quiz_history(db: Session, user_id: int):
    """Get user's quiz attempt history"""
    return db.query(models.QuizAttempt).filter(
        models.QuizAttempt.user_id == user_id
    ).order_by(models.QuizAttempt.completed_at.desc()).all()

def get_user_specialization_scores(db: Session, user_id: int):
    """Get user's average scores by specialization"""
    # This would require a more complex query to join attempts with quizzes and specializations
    # For now, return basic user scores
    user = get_user_by_id(db, user_id)
    if user:
        return {
            "readiness_score": user.readiness_score,
            "technical_score": user.technical_score,
            "soft_skills_score": user.soft_skills_score,
            "leadership_score": user.leadership_score
        }
    return None

# READINESS AND DASHBOARD OPERATIONS
def recompute_user_readiness(db: Session, user_id: int) -> Optional[Dict[str, Any]]:
    """Recompute and persist user's readiness aggregates from attempts.
    Strategy: simple average of attempt percentages; map to categories.
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    attempts = get_user_quiz_history(db, user_id)
    if not attempts:
        user.readiness_score = 0.0
        user.technical_score = 0.0
        user.soft_skills_score = 0.0
        db.commit()
        return {
            "overall": 0.0,
            "technical": 0.0,
            "soft": 0.0,
        }

    avg_percentage = sum(a.percentage for a in attempts) / len(attempts)
    overall = round(avg_percentage, 2)
    technical = round(overall * 0.9, 2)
    soft = round(overall * 0.85, 2)

    user.readiness_score = overall
    user.technical_score = technical
    user.soft_skills_score = soft
    db.commit()

    return {
        "overall": overall,
        "technical": technical,
        "soft": soft,
    }

def get_dashboard_summary(db: Session, user_id: int) -> Optional[Dict[str, Any]]:
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    # Ensure readiness is up to date
    readiness = recompute_user_readiness(db, user_id)
    attempts = get_user_quiz_history(db, user_id)
    recent = []
    for a in attempts[:5]:
        recent.append({
            "id": a.id,
            "quiz_id": a.quiz_id,
            "score": round(a.percentage, 2),
            "passed": a.is_passed,
            "completed_at": a.completed_at.isoformat() if a.completed_at else None,
        })
    return {
        "readiness": readiness or {
            "overall": user.readiness_score or 0.0,
            "technical": user.technical_score or 0.0,
            "soft": user.soft_skills_score or 0.0,
        },
        "recent_attempts": recent,
    }

def get_attempt_with_quiz(db: Session, attempt_id: int) -> Optional[Dict[str, Any]]:
    attempt = get_quiz_attempt(db, attempt_id)
    if not attempt:
        return None
    quiz = get_quiz_by_id(db, attempt.quiz_id)
    return {
        "attempt": attempt,
        "quiz": quiz,
    }

# GOAL OPERATIONS
def create_goal(db: Session, user_id: int, title: str, description: str, category: str, target_value: float, target_date: Optional[datetime] = None):
    """Create a new goal for a user"""
    goal = models.Goal(
        user_id=user_id,
        title=title,
        description=description,
        category=category,
        target_value=target_value,
        current_value=0.0,
        is_completed=False,
        target_date=target_date
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal

def get_user_goals(db: Session, user_id: int):
    """Get all goals for a user"""
    return db.query(models.Goal).filter(
        models.Goal.user_id == user_id
    ).order_by(models.Goal.created_at.desc()).all()

def update_goal(db: Session, goal_id: int, user_id: int, **kwargs):
    """Update a goal"""
    goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == user_id
    ).first()
    if not goal:
        return None
    for key, value in kwargs.items():
        if hasattr(goal, key):
            setattr(goal, key, value)
    db.commit()
    db.refresh(goal)
    return goal

def delete_goal(db: Session, goal_id: int, user_id: int):
    """Delete a goal"""
    goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == user_id
    ).first()
    if not goal:
        return False
    db.delete(goal)
    db.commit()
    return True

def auto_update_goals_on_quiz_completion(db: Session, user_id: int):
    """
    Automatically update user goals based on their current readiness scores
    Called after quiz completion to sync goals with actual progress
    """
    try:
        # Get current readiness scores
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            return
        
        # Get all active (not completed) goals for this user
        active_goals = db.query(models.Goal).filter(
            models.Goal.user_id == user_id,
            models.Goal.is_completed == False
        ).all()
        
        updated_goals = []
        
        for goal in active_goals:
            # Map goal category to user score field
            score_mapping = {
                'readiness': user.readiness_score,
                'technical': user.technical_score,
                'soft_skills': user.soft_skills_score,
                'leadership': user.leadership_score
            }
            
            # Get the corresponding score for this goal category
            current_score = score_mapping.get(goal.category)
            
            if current_score is not None:
                # Update the goal's current value to match the user's actual score
                old_value = goal.current_value
                goal.current_value = current_score
                
                # Check if goal is now completed
                if goal.current_value >= goal.target_value and not goal.is_completed:
                    goal.is_completed = True
                    updated_goals.append({
                        'id': goal.id,
                        'title': goal.title,
                        'category': goal.category,
                        'completed': True,
                        'progress': goal.current_value
                    })
                elif old_value != current_score:
                    updated_goals.append({
                        'id': goal.id,
                        'title': goal.title,
                        'category': goal.category,
                        'completed': False,
                        'progress': goal.current_value
                    })
        
        db.commit()
        return updated_goals
        
    except Exception as e:
        print(f"Error auto-updating goals: {e}")
        db.rollback()
        return []

# JOURNAL ENTRY OPERATIONS
def create_journal_entry(db: Session, user_id: int, content: str, prompt: Optional[str] = None):
    """Create a new journal entry"""
    entry = models.JournalEntry(
        user_id=user_id,
        content=content,
        prompt=prompt
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

def get_user_journal_entries(db: Session, user_id: int, limit: int = 20):
    """Get journal entries for a user"""
    return db.query(models.JournalEntry).filter(
        models.JournalEntry.user_id == user_id
    ).order_by(models.JournalEntry.entry_date.desc()).limit(limit).all()

def update_journal_entry(db: Session, entry_id: int, user_id: int, content: str):
    """Update a journal entry"""
    entry = db.query(models.JournalEntry).filter(
        models.JournalEntry.id == entry_id,
        models.JournalEntry.user_id == user_id
    ).first()
    if not entry:
        return None
    entry.content = content
    db.commit()
    db.refresh(entry)
    return entry

def delete_journal_entry(db: Session, entry_id: int, user_id: int):
    """Delete a journal entry"""
    entry = db.query(models.JournalEntry).filter(
        models.JournalEntry.id == entry_id,
        models.JournalEntry.user_id == user_id
    ).first()
    if not entry:
        return False
    db.delete(entry)
    db.commit()
    return True

# FEEDBACK OPERATIONS
def create_feedback(db: Session, feedback: schemas.FeedbackCreate) -> models.Feedback:
    """Create a new feedback entry"""
    db_feedback = models.Feedback(**feedback.dict())
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

def submit_quiz_answers(db: Session, attempt_id: int, answers: List[schemas.QuizAnswer]) -> dict:
    """
    Submit quiz answers and calculate detailed score with personalized feedback.
    This is the superior merged function combining detailed feedback with sophisticated scoring.
    """
    attempt = db.query(models.QuizAttempt).filter(models.QuizAttempt.id == attempt_id).first()
    if not attempt:
        return None
    
    quiz = get_quiz_by_id(db, attempt.quiz_id)
    if not quiz:
        return None
    
    # Initialize scoring variables (using points-based system)
    correct_count = 0
    total_questions = 0
    total_points = 0
    earned_points = 0
    question_results = []  # Store detailed results for each question
    
    # Process each answer
    for answer_data in answers:
        question = db.query(models.Question).filter(
            models.Question.id == answer_data.question_id
        ).first()
        
        if question:
            total_questions += 1
            total_points += question.points  # Use weighted points system
            
            # Check if answer is correct
            is_correct = False
            user_answer = answer_data.selected_answer
            
            # Method 1: Check against QuestionOption model
            if question.options:
                for option in question.options:
                    # The selected_answer could be either the option text or a letter (A, B, C, D)
                    if option.is_correct:
                        # Check if user's answer matches the correct option text
                        if option.option_text == user_answer:
                            is_correct = True
                            earned_points += question.points
                            correct_count += 1
                            break
            
            # Store detailed result for this question
            # Build options dict from QuestionOption relationships
            options_dict = {}
            if question.options:
                # Sort by order_index to maintain A, B, C, D order
                sorted_options = sorted(question.options, key=lambda x: x.order_index)
                option_letters = ['A', 'B', 'C', 'D', 'E', 'F']
                for idx, option in enumerate(sorted_options):
                    if idx < len(option_letters):
                        options_dict[option_letters[idx]] = option.option_text
            
            question_results.append({
                "question_id": question.id,
                "question_text": question.question_text,
                "user_answer": user_answer,
                "correct_answer": next((opt.option_text for opt in question.options if opt.is_correct), None),
                "is_correct": is_correct,
                "points": question.points,
                "earned_points": question.points if is_correct else 0,
                "explanation": question.explanation if hasattr(question, 'explanation') else None,
                "options": options_dict
            })
    
    # Calculate scores using points-based system
    max_score = float(total_points) if total_points > 0 else 1.0
    score = float(earned_points)
    percentage = (score / max_score * 100) if max_score > 0 else 0.0
    
    # Get quiz passing score (flexible, not hardcoded)
    passing_score = quiz.passing_score if hasattr(quiz, 'passing_score') and quiz.passing_score else 70.0
    is_passed = percentage >= passing_score
    
    # Update attempt with comprehensive results
    attempt.score = score
    attempt.max_score = max_score
    attempt.percentage = percentage
    attempt.is_passed = is_passed
    attempt.is_completed = True
    attempt.completed_at = datetime.now(timezone.utc)
    
    # Update user's readiness scores based on quiz category
    user = get_user_by_id(db, attempt.user_id)
    score_impact = None
    
    if user and quiz.specialization:
        # Calculate score impact based on performance
        score_increase = int(percentage / 20)  # Max 5 points increase
        
        # Update technical score (you can categorize quizzes differently)
        old_technical = user.technical_score or 0
        user.technical_score = min(100, (user.technical_score or 0) + score_increase)
        
        # Recalculate overall readiness score
        user.readiness_score = int(
            ((user.technical_score or 0) * 0.5) + 
            ((user.soft_skills_score or 0) * 0.3) + 
            ((user.leadership_score or 0) * 0.2)
        )
        
        score_impact = {
            "category": "Technical Skills",
            "old_score": old_technical,
            "new_score": user.technical_score,
            "increase": user.technical_score - old_technical
        }

