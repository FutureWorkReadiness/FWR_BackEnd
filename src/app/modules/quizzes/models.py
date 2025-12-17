"""
Quiz, Question, QuestionOption, and QuizAttempt models.
Defines the quiz system structure and user attempts.
"""

import uuid
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.app.db.base import Base


class Quiz(Base):
    """
    Quizzes for each specialization with difficulty levels.
    Each specialization can have multiple quizzes of varying difficulty.
    """

    __tablename__ = "quizzes"

    quiz_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    specialization_id = Column(
        UUID(as_uuid=True), ForeignKey("specializations.specialization_id"), nullable=False
    )
    difficulty_level = Column(Integer, nullable=False)  # 1, 2, 3, 4, or 5
    is_active = Column(Boolean, default=True)
    time_limit_minutes = Column(Integer, default=30)
    passing_score = Column(Float, default=70.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    specialization = relationship("Specialization", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")


class Question(Base):
    """
    Questions within quizzes.
    Supports multiple choice, true/false, and short answer types.
    """

    __tablename__ = "questions"

    question_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.quiz_id"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False)  # 'multiple_choice', 'true_false', 'short_answer'
    points = Column(Integer, default=1)
    order_index = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    explanation = Column(Text, nullable=True)  # Explanation shown after answer
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan")


class QuestionOption(Base):
    """
    Options for multiple choice questions.
    One option per question should be marked as correct.
    """

    __tablename__ = "question_options"

    option_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.question_id"), nullable=False)
    option_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)
    order_index = Column(Integer, nullable=False)  # A=0, B=1, C=2, D=3
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    question = relationship("Question", back_populates="options")


class QuizAttempt(Base):
    """
    User attempts at quizzes.
    Tracks score, timing, and pass/fail status.
    """

    __tablename__ = "quiz_attempts"

    attempt_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.quiz_id"), nullable=False)
    score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False)
    percentage = Column(Float, nullable=False)
    time_taken_minutes = Column(Integer, nullable=True)
    is_passed = Column(Boolean, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="quiz_attempts")
    quiz = relationship("Quiz", back_populates="attempts")

