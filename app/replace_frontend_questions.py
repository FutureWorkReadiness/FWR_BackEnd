#!/usr/bin/env python3
"""
Database Integration Script - Replace Frontend Development Questions
Generates AI questions and replaces existing ones in the database
"""
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Specialization, Quiz, Question, QuestionOption
from app.generate_quiz import generate_full_quiz


def get_frontend_specialization(db: Session):
    """Find the Frontend Development specialization"""
    spec = db.query(Specialization).filter(
        Specialization.name.ilike("%frontend%")
    ).first()
    
    if not spec:
        print("❌ Frontend Development specialization not found in database!")
        print("Available specializations:")
        all_specs = db.query(Specialization).all()
        for s in all_specs:
            print(f"  - {s.name} (ID: {s.id})")
        return None
    
    print(f"✅ Found specialization: {spec.name} (ID: {spec.id})")
    return spec


def get_or_create_quiz(db: Session, spec_id: int, difficulty: int, title: str):
    """Get existing quiz or create a new one"""
    quiz = db.query(Quiz).filter(
        Quiz.specialization_id == spec_id,
        Quiz.difficulty_level == difficulty
    ).first()
    
    if quiz:
        print(f"✅ Found existing quiz: {quiz.title} (ID: {quiz.id})")
        return quiz
    
    # Create new quiz
    quiz = Quiz(
        title=title,
        description=f"AI-generated quiz for {title}",
        specialization_id=spec_id,
        difficulty_level=difficulty,
        is_active=True,
        time_limit_minutes=30,
        passing_score=70.0
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    print(f"✅ Created new quiz: {quiz.title} (ID: {quiz.id})")
    return quiz


def delete_existing_questions(db: Session, quiz_id: int):
    """Delete all existing questions and options for a quiz"""
    # First delete all options
    questions = db.query(Question).filter(Question.quiz_id == quiz_id).all()
    total_options = 0
    for question in questions:
        options_count = db.query(QuestionOption).filter(
            QuestionOption.question_id == question.id
        ).count()
        total_options += options_count
        db.query(QuestionOption).filter(
            QuestionOption.question_id == question.id
        ).delete()
    
    # Then delete questions
    questions_count = db.query(Question).filter(Question.quiz_id == quiz_id).count()
    db.query(Question).filter(Question.quiz_id == quiz_id).delete()
    db.commit()
    
    print(f"🗑️  Deleted {questions_count} existing questions and {total_options} options")


def insert_ai_questions(db: Session, quiz_id: int, ai_questions: list):
    """Insert AI-generated questions into the database"""
    print(f"\n📥 Inserting {len(ai_questions)} AI-generated questions...")
    
    for idx, q_data in enumerate(ai_questions, 1):
        # Create question
        question = Question(
            quiz_id=quiz_id,
            question_text=q_data['question'],
            question_type='multiple_choice',
            points=1,
            order_index=idx,
            is_active=True,
            explanation=q_data.get('explanation', '')
        )
        db.add(question)
        db.flush()  # Get the question ID
        
        # Create options
        for opt_data in q_data['options']:
            option = QuestionOption(
                question_id=question.id,
                option_text=opt_data['text'],
                is_correct=(opt_data['id'] == q_data['correct_answer']),
                order_index=ord(opt_data['id']) - ord('A')  # A=0, B=1, C=2, D=3
            )
            db.add(option)
        
        print(f"  ✅ Question {idx}/{len(ai_questions)}: {q_data['topic']}")
    
    db.commit()
    print(f"✅ All {len(ai_questions)} questions inserted successfully!")


def main():
    """Main execution flow"""
    print("=" * 70)
    print("DATABASE INTEGRATION: Replace Frontend Development Questions")
    print("=" * 70)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Step 1: Find Frontend Development specialization
        print("\n[STEP 1] Finding Frontend Development specialization...")
        frontend_spec = get_frontend_specialization(db)
        if not frontend_spec:
            return
        
        # Step 2: Generate AI questions
        print("\n[STEP 2] Generating AI questions...")
        topics = [
            "React Hooks",
            "State Management", 
            "Component Lifecycle"
        ]
        
        questions = generate_full_quiz(
            specialization="Frontend Development",
            topics=topics,
            questions_per_topic=2,
            difficulty=3  # Advanced level
        )
        
        if not questions:
            print("❌ Failed to generate questions!")
            return
        
        print(f"✅ Generated {len(questions)} questions successfully!")
        
        # Step 3: Get or create quiz
        print("\n[STEP 3] Setting up quiz in database...")
        quiz = get_or_create_quiz(
            db,
            frontend_spec.id,
            difficulty=3,
            title="Frontend Development - Advanced Assessment"
        )
        
        # Step 4: Delete old questions
        print("\n[STEP 4] Removing old questions...")
        delete_existing_questions(db, quiz.id)
        
        # Step 5: Insert new AI questions
        print("\n[STEP 5] Inserting AI-generated questions...")
        insert_ai_questions(db, quiz.id, questions)
        
        # Step 6: Verify
        print("\n[STEP 6] Verification...")
        final_count = db.query(Question).filter(Question.quiz_id == quiz.id).count()
        options_count = db.query(QuestionOption).join(Question).filter(
            Question.quiz_id == quiz.id
        ).count()
        
        print(f"✅ Quiz now has {final_count} questions with {options_count} total options")
        
        print("\n" + "=" * 70)
        print("✅ SUCCESS! Frontend Development questions replaced with AI content!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
