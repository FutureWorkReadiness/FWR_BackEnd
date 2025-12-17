"""
Quizzes module.
Handles quiz, question, and attempt domain logic.
"""

from src.app.modules.quizzes.models import Quiz, Question, QuestionOption, QuizAttempt
from src.app.modules.quizzes.service import QuizService

__all__ = ["Quiz", "Question", "QuestionOption", "QuizAttempt", "QuizService"]

