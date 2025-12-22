"""
Quiz service - handles quiz-related business logic.

Updated for new question format (v2):
- Options have key (A-E), text, is_correct, rationale
- Users submit answers by key (A, B, C, D, E)
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from uuid import UUID

from src.app.modules.quizzes.models import Quiz, Question, QuestionOption, QuizAttempt
from src.app.modules.users.models import User
from src.app.modules.sectors.models import Specialization
from src.app.modules.quizzes.schema import QuizAnswer


class QuizService:
    """Service class for quiz-related operations."""

    # ============================================================
    # QUIZ OPERATIONS
    # ============================================================

    @staticmethod
    def get_all_quizzes(db: Session) -> List[Quiz]:
        """Get all quizzes with their specializations."""
        return db.query(Quiz).join(Specialization).all()

    @staticmethod
    def get_quiz_by_id(db: Session, quiz_id: UUID) -> Optional[Quiz]:
        """Get quiz by ID with questions and answer options."""
        return db.query(Quiz).filter(Quiz.quiz_id == quiz_id).first()

    @staticmethod
    def get_quizzes_by_specialization(
        db: Session, specialization_id: UUID
    ) -> List[Quiz]:
        """Get all quizzes for a specialization."""
        return db.query(Quiz).filter(Quiz.specialization_id == specialization_id).all()

    @staticmethod
    def get_quiz_questions(db: Session, quiz_id: UUID) -> List[Question]:
        """Get all questions for a quiz with their answer options."""
        return (
            db.query(Question)
            .filter(Question.quiz_id == quiz_id)
            .order_by(Question.order_index)
            .all()
        )

    @staticmethod
    def get_quiz_count_by_specialization(db: Session, specialization_id: UUID) -> int:
        """Get the count of quizzes for a specialization."""
        return (
            db.query(Quiz).filter(Quiz.specialization_id == specialization_id).count()
        )

    # ============================================================
    # QUIZ ATTEMPT OPERATIONS
    # ============================================================

    @staticmethod
    def create_quiz_attempt(db: Session, user_id: UUID, quiz_id: UUID) -> QuizAttempt:
        """Create a new quiz attempt."""
        db_attempt = QuizAttempt(
            user_id=user_id,
            quiz_id=quiz_id,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),  # Will be updated on submission
            score=0.0,
            max_score=0.0,
            percentage=0.0,
            is_passed=False,
        )
        db.add(db_attempt)
        db.commit()
        db.refresh(db_attempt)
        return db_attempt

    @staticmethod
    def get_quiz_attempt(db: Session, attempt_id: UUID) -> Optional[QuizAttempt]:
        """Get quiz attempt by ID."""
        return (
            db.query(QuizAttempt).filter(QuizAttempt.attempt_id == attempt_id).first()
        )

    @staticmethod
    def get_user_quiz_history(db: Session, user_id: UUID) -> List[QuizAttempt]:
        """Get user's quiz attempt history."""
        return (
            db.query(QuizAttempt)
            .filter(QuizAttempt.user_id == user_id)
            .order_by(QuizAttempt.completed_at.desc())
            .all()
        )

    @staticmethod
    def get_attempt_with_quiz(
        db: Session, attempt_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Get attempt with associated quiz."""
        attempt = QuizService.get_quiz_attempt(db, attempt_id)
        if not attempt:
            return None
        quiz = QuizService.get_quiz_by_id(db, attempt.quiz_id)
        return {
            "attempt": attempt,
            "quiz": quiz,
        }

    @staticmethod
    def get_quiz_attempt_count(db: Session) -> int:
        """Get total count of quiz attempts."""
        return db.query(QuizAttempt).count()

    # ============================================================
    # QUIZ SCORING AND SUBMISSION
    # ============================================================

    @staticmethod
    def submit_quiz_answers(
        db: Session, attempt_id: UUID, answers: List[QuizAnswer]
    ) -> Optional[Dict[str, Any]]:
        """
        Submit quiz answers and calculate detailed score with personalized feedback.

        Users submit answers by option key (A, B, C, D, E).
        """
        attempt = (
            db.query(QuizAttempt).filter(QuizAttempt.attempt_id == attempt_id).first()
        )
        if not attempt:
            return None

        quiz = QuizService.get_quiz_by_id(db, attempt.quiz_id)
        if not quiz:
            return None

        # Initialize scoring variables
        correct_count = 0
        total_questions = 0
        total_points = 0
        earned_points = 0
        question_results = []

        # Process each answer
        for answer_data in answers:
            question = (
                db.query(Question)
                .filter(Question.question_id == answer_data.question_id)
                .first()
            )

            if question:
                total_questions += 1
                total_points += question.points

                # Get user's selected key (A, B, C, D, or E)
                selected_key = answer_data.selected_key.upper()

                # Find the correct answer key and check if user is correct
                is_correct = False
                correct_key = None
                selected_option_text = None

                # Sort options by order_index to ensure consistent ordering
                sorted_options = sorted(question.options, key=lambda x: x.order_index)

                for option in sorted_options:
                    if option.is_correct:
                        correct_key = option.key
                    if option.key == selected_key:
                        selected_option_text = option.text
                        if option.is_correct:
                            is_correct = True
                            earned_points += question.points
                            correct_count += 1

                # Build options list for response
                options_list = []
                for option in sorted_options:
                    options_list.append(
                        {
                            "key": option.key,
                            "text": option.text,
                            "is_correct": option.is_correct,
                            "rationale": option.rationale,
                        }
                    )

                question_results.append(
                    {
                        "question_id": str(question.question_id),
                        "question_text": question.question_text,
                        "user_answer": selected_key,
                        "correct_answer": correct_key,
                        "is_correct": is_correct,
                        "points": question.points,
                        "earned_points": question.points if is_correct else 0,
                        "explanation": question.explanation,
                        "options": options_list,
                    }
                )

        # Calculate scores
        max_score = float(total_points) if total_points > 0 else 1.0
        score = float(earned_points)
        percentage = (score / max_score * 100) if max_score > 0 else 0.0

        # Get quiz passing score
        passing_score = quiz.passing_score if quiz.passing_score else 70.0
        is_passed = percentage >= passing_score

        # Calculate time taken
        time_taken = None
        if attempt.started_at:
            time_diff = datetime.now(timezone.utc) - attempt.started_at.replace(
                tzinfo=timezone.utc
            )
            time_taken = int(time_diff.total_seconds() / 60)

        # Update attempt
        attempt.score = score
        attempt.max_score = max_score
        attempt.percentage = percentage
        attempt.is_passed = is_passed
        attempt.completed_at = datetime.now(timezone.utc)
        attempt.time_taken_minutes = time_taken

        # Update user's readiness scores
        user = db.query(User).filter(User.user_id == attempt.user_id).first()
        score_impact = None

        if user and quiz.specialization:
            score_increase = int(percentage / 20)  # Max 5 points increase

            old_technical = user.technical_score or 0
            user.technical_score = min(
                100, (user.technical_score or 0) + score_increase
            )

            # Recalculate overall readiness score
            user.readiness_score = int(
                ((user.technical_score or 0) * 0.5)
                + ((user.soft_skills_score or 0) * 0.3)
                + ((user.leadership_score or 0) * 0.2)
            )

            score_impact = {
                "category": "Technical Skills",
                "old_score": old_technical,
                "new_score": user.technical_score,
                "increase": user.technical_score - old_technical,
            }

        db.commit()

        # Generate personalized feedback
        feedback = QuizService._generate_feedback(
            percentage, correct_count, total_questions, question_results
        )

        return {
            "score": percentage,
            "raw_score": score,
            "max_score": max_score,
            "correct": correct_count,
            "total": total_questions,
            "passed": is_passed,
            "passing_score": passing_score,
            "time_taken_minutes": time_taken,
            "question_results": question_results,
            "score_impact": score_impact,
            "feedback": feedback,
            "quiz_title": quiz.title,
        }

    @staticmethod
    def _generate_feedback(
        score: float, correct: int, total: int, question_results: list
    ) -> dict:
        """Generate personalized feedback based on performance."""

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

        # Find areas of weakness
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
                "Focus on the questions you got wrong",
            ]
        elif score < 90:
            recommendations = [
                "You're doing well! Focus on the few areas you missed",
                "Try more advanced quizzes in this category",
                "Review edge cases and advanced concepts",
            ]
        else:
            recommendations = [
                "Outstanding! Consider exploring advanced topics",
                "Help others by sharing your knowledge",
                "Try quizzes in related specializations",
            ]

        return {
            "overall": overall,
            "strengths": f"You correctly answered {correct} out of {total} questions.",
            "weaknesses": weakness_topics,
            "recommendations": recommendations,
        }

    # ============================================================
    # READINESS AND DASHBOARD OPERATIONS
    # ============================================================

    @staticmethod
    def recompute_user_readiness(
        db: Session, user_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Recompute and persist user's readiness aggregates from attempts."""
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return None

        attempts = QuizService.get_user_quiz_history(db, user_id)
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

    @staticmethod
    def get_dashboard_summary(db: Session, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Get dashboard summary for a user."""
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return None

        # Ensure readiness is up to date
        readiness = QuizService.recompute_user_readiness(db, user_id)
        attempts = QuizService.get_user_quiz_history(db, user_id)

        recent = []
        for a in attempts[:5]:
            recent.append(
                {
                    "attempt_id": str(a.attempt_id),
                    "quiz_id": str(a.quiz_id),
                    "score": round(a.percentage, 2),
                    "passed": a.is_passed,
                    "completed_at": (
                        a.completed_at.isoformat() if a.completed_at else None
                    ),
                }
            )

        return {
            "readiness": readiness
            or {
                "overall": user.readiness_score or 0.0,
                "technical": user.technical_score or 0.0,
                "soft": user.soft_skills_score or 0.0,
            },
            "recent_attempts": recent,
        }
