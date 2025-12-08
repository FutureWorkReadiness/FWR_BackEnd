"""
Database models for the Future of Work Readiness platform
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Sector(Base):
    """Main sectors (e.g., Technology, Healthcare, etc.)"""
    __tablename__ = "sectors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    specializations = relationship("Specialization", back_populates="sector")


class Specialization(Base):
    """Specializations within sectors"""
    __tablename__ = "specializations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, index=True)
    description = Column(Text, nullable=True)
    sector_id = Column(Integer, ForeignKey("sectors.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    sector = relationship("Sector", back_populates="specializations")
    quizzes = relationship("Quiz", back_populates="specialization")


class Quiz(Base):
    """Quizzes for each specialization with difficulty levels"""
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    specialization_id = Column(Integer, ForeignKey("specializations.id"), nullable=False)
    difficulty_level = Column(Integer, nullable=False)  # 1, 2, 3, or 4
    duration_minutes = Column(Integer, default=30)
    total_questions = Column(Integer, default=20)
    passing_score = Column(Float, default=70.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    specialization = relationship("Specialization", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz")
    attempts = relationship("UserQuizAttempt", back_populates="quiz")


class Question(Base):
    """Questions within quizzes"""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), default="multiple_choice")
    order_in_quiz = Column(Integer, nullable=False)
    points = Column(Integer, default=1)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    answer_options = relationship("AnswerOption", back_populates="question")
    user_answers = relationship("UserAnswer", back_populates="question")


class AnswerOption(Base):
    """Answer options for each question"""
    __tablename__ = "answer_options"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    option_text = Column(Text, nullable=False)
    option_letter = Column(String(1), nullable=False)  # A, B, C, D, E
    is_correct = Column(Boolean, default=False)
    order_in_question = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    question = relationship("Question", back_populates="answer_options")
    user_answers = relationship("UserAnswer", back_populates="selected_option")


class User(Base):
    """Users of the platform"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # User preferences and stats
    preferred_sector_id = Column(Integer, ForeignKey("sectors.id"), nullable=True)
    preferred_specialization_id = Column(Integer, ForeignKey("specializations.id"), nullable=True)
    
    # Overall readiness scores
    readiness_score = Column(Float, default=0.0)
    technical_score = Column(Float, default=0.0)
    soft_skills_score = Column(Float, default=0.0)
    leadership_score = Column(Float, default=0.0)
    
    # Relationships
    preferred_sector = relationship("Sector", foreign_keys=[preferred_sector_id])
    preferred_specialization = relationship("Specialization", foreign_keys=[preferred_specialization_id])
    quiz_attempts = relationship("UserQuizAttempt", back_populates="user")


class UserQuizAttempt(Base):
    """User attempts at quizzes"""
    __tablename__ = "user_quiz_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    
    # Attempt details
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    score = Column(Float, nullable=True)
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, default=0)
    time_taken_seconds = Column(Integer, nullable=True)
    passed = Column(Boolean, nullable=True)
    
    # Status
    status = Column(String(20), default="in_progress")
    
    # Relationships
    user = relationship("User", back_populates="quiz_attempts")
    quiz = relationship("Quiz", back_populates="attempts")
    user_answers = relationship("UserAnswer", back_populates="attempt")


class UserAnswer(Base):
    """Individual answers given by users during quiz attempts"""
    __tablename__ = "user_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("user_quiz_attempts.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    selected_option_id = Column(Integer, ForeignKey("answer_options.id"), nullable=True)
    is_correct = Column(Boolean, nullable=True)
    answered_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    attempt = relationship("UserQuizAttempt", back_populates="user_answers")
    question = relationship("Question", back_populates="user_answers")
    selected_option = relationship("AnswerOption", back_populates="user_answers")
