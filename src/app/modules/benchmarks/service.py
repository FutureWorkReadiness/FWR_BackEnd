"""
Benchmark service - handles peer benchmarking business logic.
"""

from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from uuid import UUID
import json

from src.app.modules.benchmarks.models import PeerBenchmark
from src.app.modules.users.models import User
from src.app.modules.sectors.models import Specialization


class BenchmarkService:
    """Service class for peer benchmarking operations."""

    @staticmethod
    def calculate_peer_benchmarks(db: Session, specialization_id: UUID) -> bool:
        """
        Calculate and store peer benchmark statistics for a specialization.
        This should be run periodically (e.g., daily via cron job).
        """
        # Get all users in this specialization
        users = db.query(User).filter(User.preferred_specialization_id == specialization_id).all()

        if not users or len(users) < 2:
            # Need at least 2 users for meaningful comparison
            return False

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
                "description": "Most peers excel in technical competencies",
            })
        if avg_soft_skills >= 70:
            strengths.append({
                "area": "Soft Skills",
                "percentage": round(avg_soft_skills, 1),
                "description": "Strong interpersonal and communication abilities",
            })
        if avg_leadership >= 70:
            strengths.append({
                "area": "Leadership",
                "percentage": round(avg_leadership, 1),
                "description": "Effective leadership and decision-making",
            })

        # Identify common gaps (areas where average is low)
        gaps = []
        if avg_technical < 60:
            gaps.append({
                "area": "Technical Skills",
                "percentage": round(avg_technical, 1),
                "description": "Many peers need to strengthen technical foundations",
            })
        if avg_soft_skills < 60:
            gaps.append({
                "area": "Soft Skills",
                "percentage": round(avg_soft_skills, 1),
                "description": "Communication and collaboration skills need development",
            })
        if avg_leadership < 60:
            gaps.append({
                "area": "Leadership",
                "percentage": round(avg_leadership, 1),
                "description": "Leadership capabilities require attention",
            })

        # Check if benchmark already exists
        existing = db.query(PeerBenchmark).filter(PeerBenchmark.specialization_id == specialization_id).first()

        if existing:
            # Update existing
            existing.avg_readiness_score = avg_readiness
            existing.avg_technical_score = avg_technical
            existing.avg_soft_skills_score = avg_soft_skills
            existing.avg_leadership_score = avg_leadership
            existing.total_users = total_users
            existing.median_readiness_score = median_readiness
            existing.common_strengths = json.dumps(strengths)
            existing.common_gaps = json.dumps(gaps)
            existing.last_updated = datetime.now(timezone.utc)
        else:
            # Create new
            benchmark = PeerBenchmark(
                specialization_id=specialization_id,
                avg_readiness_score=avg_readiness,
                avg_technical_score=avg_technical,
                avg_soft_skills_score=avg_soft_skills,
                avg_leadership_score=avg_leadership,
                total_users=total_users,
                median_readiness_score=median_readiness,
                common_strengths=json.dumps(strengths),
                common_gaps=json.dumps(gaps),
            )
            db.add(benchmark)

        db.commit()
        return True

    @staticmethod
    def get_peer_benchmark(db: Session, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Get peer benchmark comparison for a user."""
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user or not user.preferred_specialization_id:
            return None

        # Get or calculate benchmark for user's specialization
        benchmark = (
            db.query(PeerBenchmark).filter(PeerBenchmark.specialization_id == user.preferred_specialization_id).first()
        )

        if not benchmark:
            # Calculate benchmark if it doesn't exist
            BenchmarkService.calculate_peer_benchmarks(db, user.preferred_specialization_id)
            benchmark = (
                db.query(PeerBenchmark)
                .filter(PeerBenchmark.specialization_id == user.preferred_specialization_id)
                .first()
            )

        if not benchmark or benchmark.total_users < 2:
            return {
                "error": "Not enough data for peer comparison",
                "message": "We need at least 2 users in your specialization to provide meaningful comparisons.",
            }

        # Get specialization name
        specialization = (
            db.query(Specialization)
            .filter(Specialization.specialization_id == user.preferred_specialization_id)
            .first()
        )

        # Calculate comparisons
        comparisons = []

        # Readiness comparison
        readiness_diff = (user.readiness_score or 0) - benchmark.avg_readiness_score
        readiness_percentile = BenchmarkService._calculate_percentile(
            db, user.preferred_specialization_id, user.readiness_score or 0, "readiness"
        )
        comparisons.append({
            "category": "Overall Readiness",
            "your_score": round(user.readiness_score or 0, 1),
            "peer_average": round(benchmark.avg_readiness_score, 1),
            "difference": round(readiness_diff, 1),
            "percentile": readiness_percentile,
            "status": "above" if readiness_diff > 5 else "below" if readiness_diff < -5 else "average",
        })

        # Technical comparison
        technical_diff = (user.technical_score or 0) - benchmark.avg_technical_score
        technical_percentile = BenchmarkService._calculate_percentile(
            db, user.preferred_specialization_id, user.technical_score or 0, "technical"
        )
        comparisons.append({
            "category": "Technical Skills",
            "your_score": round(user.technical_score or 0, 1),
            "peer_average": round(benchmark.avg_technical_score, 1),
            "difference": round(technical_diff, 1),
            "percentile": technical_percentile,
            "status": "above" if technical_diff > 5 else "below" if technical_diff < -5 else "average",
        })

        # Soft Skills comparison
        soft_diff = (user.soft_skills_score or 0) - benchmark.avg_soft_skills_score
        soft_percentile = BenchmarkService._calculate_percentile(
            db, user.preferred_specialization_id, user.soft_skills_score or 0, "soft_skills"
        )
        comparisons.append({
            "category": "Soft Skills",
            "your_score": round(user.soft_skills_score or 0, 1),
            "peer_average": round(benchmark.avg_soft_skills_score, 1),
            "difference": round(soft_diff, 1),
            "percentile": soft_percentile,
            "status": "above" if soft_diff > 5 else "below" if soft_diff < -5 else "average",
        })

        # Leadership comparison
        leadership_diff = (user.leadership_score or 0) - benchmark.avg_leadership_score
        leadership_percentile = BenchmarkService._calculate_percentile(
            db, user.preferred_specialization_id, user.leadership_score or 0, "leadership"
        )
        comparisons.append({
            "category": "Leadership",
            "your_score": round(user.leadership_score or 0, 1),
            "peer_average": round(benchmark.avg_leadership_score, 1),
            "difference": round(leadership_diff, 1),
            "percentile": leadership_percentile,
            "status": "above" if leadership_diff > 5 else "below" if leadership_diff < -5 else "average",
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
            "last_updated": benchmark.last_updated.isoformat() if benchmark.last_updated else None,
        }

    @staticmethod
    def _calculate_percentile(db: Session, specialization_id: UUID, score: float, category: str) -> int:
        """
        Calculate what percentile a user's score falls into.
        e.g., 75 means "better than 75% of peers"
        """
        # Get all users in specialization
        users = db.query(User).filter(User.preferred_specialization_id == specialization_id).all()

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

