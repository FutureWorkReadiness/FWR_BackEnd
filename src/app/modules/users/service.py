"""
User service - handles user-related business logic.
"""

from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from uuid import UUID

from src.app.modules.users.models import User


class UserService:
    """Service class for user-related operations."""

    @staticmethod
    def create_user(db: Session, email: str, password: str, name: str) -> User:
        """Create a new user."""
        db_user = User(
            email=email,
            password_hash=password,  # In production, this should be hashed
            name=name,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.user_id == user_id).first()

    @staticmethod
    def update_user_specialization(db: Session, user_id: UUID, specialization_id: UUID) -> Optional[User]:
        """Update user's specialization."""
        user = db.query(User).filter(User.user_id == user_id).first()
        if user:
            user.preferred_specialization_id = specialization_id
            db.commit()
            db.refresh(user)
        return user

    @staticmethod
    def get_user_specialization_scores(db: Session, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Get user's average scores by specialization."""
        user = UserService.get_user_by_id(db, user_id)
        if user:
            return {
                "readiness_score": user.readiness_score,
                "technical_score": user.technical_score,
                "soft_skills_score": user.soft_skills_score,
                "leadership_score": user.leadership_score,
            }
        return None

    @staticmethod
    def update_user_scores(
        db: Session,
        user_id: UUID,
        readiness_score: Optional[float] = None,
        technical_score: Optional[float] = None,
        soft_skills_score: Optional[float] = None,
        leadership_score: Optional[float] = None,
    ) -> Optional[User]:
        """Update user's scores."""
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return None

        if readiness_score is not None:
            user.readiness_score = readiness_score
        if technical_score is not None:
            user.technical_score = technical_score
        if soft_skills_score is not None:
            user.soft_skills_score = soft_skills_score
        if leadership_score is not None:
            user.leadership_score = leadership_score

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_all_users(db: Session):
        """Get all users."""
        return db.query(User).all()

    @staticmethod
    def update_user(
        db: Session,
        user_id: UUID,
        name: Optional[str] = None,
        email: Optional[str] = None,
        readiness_score: Optional[float] = None,
        technical_score: Optional[float] = None,
        soft_skills_score: Optional[float] = None,
        preferred_specialization_id: Optional[UUID] = None,
    ) -> Optional[User]:
        """Update a user with provided fields."""
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return None

        if name is not None:
            user.name = name
        if email is not None:
            user.email = email
        if readiness_score is not None:
            user.readiness_score = readiness_score
        if technical_score is not None:
            user.technical_score = technical_score
        if soft_skills_score is not None:
            user.soft_skills_score = soft_skills_score
        if preferred_specialization_id is not None:
            user.preferred_specialization_id = preferred_specialization_id

        db.commit()
        db.refresh(user)
        return user

