"""
CRUD operations for database
"""

from sqlalchemy.orm import Session
from . import models_hierarchical as models
from . import schemas
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

# USER OPERATIONS
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

from datetime import datetime

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
    
    db.commit()
    
    # Generate personalized feedback
    feedback = generate_feedback(percentage, correct_count, total_questions, question_results)
    
    return {
        "score": percentage,  # Return percentage for consistency
        "raw_score": score,  # Include raw points scored
        "max_score": max_score,  # Include maximum possible points
        "correct": correct_count,
        "total": total_questions,
        "passed": is_passed,
        "passing_score": passing_score,
        "question_results": question_results,
        "score_impact": score_impact,
        "feedback": feedback,
        "quiz_title": quiz.title
    }


def generate_feedback(score: float, correct: int, total: int, question_results: list) -> dict:
    """Generate personalized feedback based on performance"""
    
    # Overall performance message
    if score >= 90:
        overall = "Excellent work! You have a strong understanding of this topic."
    elif score >= 80:
        overall = "Great job! You're on the right track with solid fundamentals."
    elif score >= 70:
        overall = "Good effort! You passed, but there's room for improvement."
    elif score >= 60:
        overall = "You're getting there! Review the material and try again."
    else:
        overall = "Keep practicing! Review the fundamentals and take your time."
    
    # Find areas of strength and weakness
    incorrect_questions = [q for q in question_results if not q["is_correct"]]
    
    if len(incorrect_questions) > 0:
        weakness_topics = f"Focus on reviewing: {', '.join([q['question_text'][:50] + '...' for q in incorrect_questions[:3]])}"
    else:
        weakness_topics = "You answered all questions correctly! Excellent mastery."
    
    # Recommendations
    if score < 70:
        recommendations = [
            "Review the study materials for this topic",
            "Try taking practice quizzes to reinforce learning",
            "Focus on the questions you got wrong"
        ]
    elif score < 90:
        recommendations = [
            "You're doing well! Focus on the few areas you missed",
            "Try more advanced quizzes in this category",
            "Review edge cases and advanced concepts"
        ]
    else:
        recommendations = [
            "Outstanding! Consider exploring advanced topics",
            "Help others by sharing your knowledge",
            "Try quizzes in related specializations"
        ]
    
    return {
        "overall": overall,
        "strengths": f"You correctly answered {correct} out of {total} questions.",
        "weaknesses": weakness_topics,
        "recommendations": recommendations
    }


# PEER BENCHMARKING OPERATIONS
import json
from typing import List

def calculate_peer_benchmarks(db: Session, specialization_id: int):
    """
    Calculate and store peer benchmark statistics for a specialization
    This should be run periodically (e.g., daily via cron job)
    """
    from sqlalchemy import func
    
    # Get all users in this specialization
    users = db.query(models.User).filter(
        models.User.preferred_specialization_id == specialization_id
    ).all()
    
    if not users or len(users) < 2:
        # Need at least 2 users for meaningful comparison
        return None
    
    # Calculate averages
    total_users = len(users)
    avg_readiness = sum(u.readiness_score or 0 for u in users) / total_users
    avg_technical = sum(u.technical_score or 0 for u in users) / total_users
    avg_soft_skills = sum(u.soft_skills_score or 0 for u in users) / total_users
    avg_leadership = sum(u.leadership_score or 0 for u in users) / total_users
    
    # Calculate median
    readiness_scores = sorted([u.readiness_score or 0 for u in users])
    median_readiness = readiness_scores[len(readiness_scores) // 2]
    
    # Identify common strengths (areas where average is high)
    strengths = []
    if avg_technical >= 70:
        strengths.append({
            "area": "Technical Skills",
            "percentage": round(avg_technical, 1),
            "description": "Most peers excel in technical competencies"
        })
    if avg_soft_skills >= 70:
        strengths.append({
            "area": "Soft Skills",
            "percentage": round(avg_soft_skills, 1),
            "description": "Strong interpersonal and communication abilities"
        })
    if avg_leadership >= 70:
        strengths.append({
            "area": "Leadership",
            "percentage": round(avg_leadership, 1),
            "description": "Effective leadership and decision-making"
        })
    
    # Identify common gaps (areas where average is low)
    gaps = []
    if avg_technical < 60:
        gaps.append({
            "area": "Technical Skills",
            "percentage": round(avg_technical, 1),
            "description": "Many peers need to strengthen technical foundations"
        })
    if avg_soft_skills < 60:
        gaps.append({
            "area": "Soft Skills",
            "percentage": round(avg_soft_skills, 1),
            "description": "Communication and collaboration skills need development"
        })
    if avg_leadership < 60:
        gaps.append({
            "area": "Leadership",
            "percentage": round(avg_leadership, 1),
            "description": "Leadership capabilities require attention"
        })
    
    # Check if benchmark already exists
    existing = db.query(models.PeerBenchmark).filter(
        models.PeerBenchmark.specialization_id == specialization_id
    ).first()
    
    if existing:
        # Update existing
        existing.avg_readiness = avg_readiness
        existing.avg_technical = avg_technical
        existing.avg_soft_skills = avg_soft_skills
        existing.avg_leadership = avg_leadership
        existing.total_users = total_users
        existing.median_readiness = median_readiness
        existing.common_strengths = json.dumps(strengths)
        existing.common_gaps = json.dumps(gaps)
        existing.last_updated = datetime.now(timezone.utc)
    else:
        # Create new
        benchmark = models.PeerBenchmark(
            specialization_id=specialization_id,
            avg_readiness=avg_readiness,
            avg_technical=avg_technical,
            avg_soft_skills=avg_soft_skills,
            avg_leadership=avg_leadership,
            total_users=total_users,
            median_readiness=median_readiness,
            common_strengths=json.dumps(strengths),
            common_gaps=json.dumps(gaps)
        )
        db.add(benchmark)
    
    db.commit()
    return True


def get_peer_benchmark(db: Session, user_id: int) -> Optional[Dict[str, Any]]:
    """
    Get peer benchmark comparison for a user
    """
    user = get_user_by_id(db, user_id)
    if not user or not user.preferred_specialization_id:
        return None
    
    # Get or calculate benchmark for user's specialization
    benchmark = db.query(models.PeerBenchmark).filter(
        models.PeerBenchmark.specialization_id == user.preferred_specialization_id
    ).first()
    
    if not benchmark:
        # Calculate benchmark if it doesn't exist
        calculate_peer_benchmarks(db, user.preferred_specialization_id)
        benchmark = db.query(models.PeerBenchmark).filter(
            models.PeerBenchmark.specialization_id == user.preferred_specialization_id
        ).first()
    
    if not benchmark or benchmark.total_users < 2:
        return {
            "error": "Not enough data for peer comparison",
            "message": "We need at least 2 users in your specialization to provide meaningful comparisons."
        }
    
    # Get specialization name
    specialization = db.query(models.Specialization).filter(
        models.Specialization.id == user.preferred_specialization_id
    ).first()
    
    # Calculate comparisons
    comparisons = []
    
    # Readiness comparison
    readiness_diff = (user.readiness_score or 0) - benchmark.avg_readiness
    readiness_percentile = calculate_percentile(
        db, user.preferred_specialization_id, user.readiness_score or 0, "readiness"
    )
    comparisons.append({
        "category": "Overall Readiness",
        "your_score": round(user.readiness_score or 0, 1),
        "peer_average": round(benchmark.avg_readiness, 1),
        "difference": round(readiness_diff, 1),
        "percentile": readiness_percentile,
        "status": "above" if readiness_diff > 5 else "below" if readiness_diff < -5 else "average"
    })
    
    # Technical comparison
    technical_diff = (user.technical_score or 0) - benchmark.avg_technical
    technical_percentile = calculate_percentile(
        db, user.preferred_specialization_id, user.technical_score or 0, "technical"
    )
    comparisons.append({
        "category": "Technical Skills",
        "your_score": round(user.technical_score or 0, 1),
        "peer_average": round(benchmark.avg_technical, 1),
        "difference": round(technical_diff, 1),
        "percentile": technical_percentile,
        "status": "above" if technical_diff > 5 else "below" if technical_diff < -5 else "average"
    })
    
    # Soft Skills comparison
    soft_diff = (user.soft_skills_score or 0) - benchmark.avg_soft_skills
    soft_percentile = calculate_percentile(
        db, user.preferred_specialization_id, user.soft_skills_score or 0, "soft_skills"
    )
    comparisons.append({
        "category": "Soft Skills",
        "your_score": round(user.soft_skills_score or 0, 1),
        "peer_average": round(benchmark.avg_soft_skills, 1),
        "difference": round(soft_diff, 1),
        "percentile": soft_percentile,
        "status": "above" if soft_diff > 5 else "below" if soft_diff < -5 else "average"
    })
    
    # Leadership comparison
    leadership_diff = (user.leadership_score or 0) - benchmark.avg_leadership
    leadership_percentile = calculate_percentile(
        db, user.preferred_specialization_id, user.leadership_score or 0, "leadership"
    )
    comparisons.append({
        "category": "Leadership",
        "your_score": round(user.leadership_score or 0, 1),
        "peer_average": round(benchmark.avg_leadership, 1),
        "difference": round(leadership_diff, 1),
        "percentile": leadership_percentile,
        "status": "above" if leadership_diff > 5 else "below" if leadership_diff < -5 else "average"
    })
    
    # Parse common strengths and gaps
    strengths = json.loads(benchmark.common_strengths) if benchmark.common_strengths else []
    gaps = json.loads(benchmark.common_gaps) if benchmark.common_gaps else []
    
    return {
        "specialization_name": specialization.name if specialization else "Your Specialization",
        "total_peers": benchmark.total_users - 1,  # Exclude the user themselves
        "comparisons": comparisons,
        "overall_percentile": readiness_percentile,
        "common_strengths": strengths,
        "common_gaps": gaps,
        "last_updated": benchmark.last_updated.isoformat() if benchmark.last_updated else None
    }


def calculate_percentile(db: Session, specialization_id: int, score: float, category: str) -> int:
    """
    Calculate what percentile a user's score falls into
    e.g., 75 means "better than 75% of peers"
    """
    # Get all users in specialization
    users = db.query(models.User).filter(
        models.User.preferred_specialization_id == specialization_id
    ).all()
    
    if not users or len(users) < 2:
        return 50  # Default to 50th percentile if not enough data
    
    # Get scores based on category
    if category == "readiness":
        scores = [u.readiness_score or 0 for u in users]
    elif category == "technical":
        scores = [u.technical_score or 0 for u in users]
    elif category == "soft_skills":
        scores = [u.soft_skills_score or 0 for u in users]
    elif category == "leadership":
        scores = [u.leadership_score or 0 for u in users]
    else:
        return 50
    
    # Count how many scores are below this user's score
    below_count = sum(1 for s in scores if s < score)
    
    # Calculate percentile
    percentile = int((below_count / len(scores)) * 100)
    
    return percentile

