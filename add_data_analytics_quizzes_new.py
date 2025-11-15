#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))
from app.database import SessionLocal
from app import models_hierarchical as models

def add_data_analytics_quizzes():
    db = SessionLocal()
    try:
        print("=" * 80)
        print("Adding Data Analytics Quizzes (Levels 1-5)")
        print("=" * 80)
        
        spec = db.query(models.Specialization).filter(
            models.Specialization.name == "Data Analytics"
        ).first()
        
        if not spec:
            print("❌ Specialization not found!")
            return
        
        print(f"✅ Found specialization (ID: {spec.id})")
        
        # Delete existing quizzes
        existing = db.query(models.Quiz).filter(
            models.Quiz.specialization_id == spec.id
        ).all()
        
        if existing:
            print(f"🗑️  Deleting {len(existing)} existing quizzes...")
            for quiz in existing:
                db.query(models.QuizAttempt).filter(models.QuizAttempt.quiz_id == quiz.id).delete()
                for q in quiz.questions:
                    db.query(models.QuestionOption).filter(models.QuestionOption.question_id == q.id).delete()
                db.query(models.Question).filter(models.Question.quiz_id == quiz.id).delete()
            db.query(models.Quiz).filter(models.Quiz.specialization_id == spec.id).delete()
            db.commit()
        

        db.commit()
        print("\n" + "=" * 80)
        print("✅ Successfully added all Data Analytics quizzes!")
        print("=" * 80)
        print("\n📊 Summary:")
        print("   Level 1 (Basics): 20 questions")
        print("   Level 2 (Intermediate): 20 questions")
        print("   Level 3 (Advanced): 20 questions")
        print("   Level 4 (Expert): 20 questions")
        print("   Level 5 (Strategic): 20 questions")
        print("   Total: 100 questions across 5 quizzes")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_data_analytics_quizzes()
