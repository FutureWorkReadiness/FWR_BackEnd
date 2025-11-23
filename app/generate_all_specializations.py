#!/usr/bin/env python3
"""
Generate AI quiz questions for ALL specializations and ALL difficulty levels
"""
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Specialization, Quiz, Question, QuestionOption
from app.generate_quiz import generate_quiz_question


# Specialization configurations (topics only - we'll loop through all difficulties)
SPECIALIZATIONS_CONFIG = {
    "Frontend Development": {
        "topics": ["React Hooks", "State Management", "Component Lifecycle"],
        "questions_per_topic": 2
    },
    "Backend Development": {
        "topics": ["RESTful APIs", "Database Design", "Authentication & Authorization"],
        "questions_per_topic": 2
    },
    "Data Science": {
        "topics": ["Data Analysis", "Machine Learning Basics", "Data Visualization"],
        "questions_per_topic": 2
    },
    "Cybersecurity": {
        "topics": ["Network Security", "Threat Analysis", "Security Best Practices"],
        "questions_per_topic": 2
    },
    "DevOps Engineering": {
        "topics": ["CI/CD Pipelines", "Container Orchestration", "Infrastructure as Code"],
        "questions_per_topic": 2
    },
    "Mobile Development": {
        "topics": ["Mobile UI Design", "State Management", "Native vs Cross-Platform"],
        "questions_per_topic": 2
    }
}

# All 5 difficulty levels
DIFFICULTY_LEVELS = [1, 2, 3, 4, 5]  # 1=Beginner, 2=Intermediate, 3=Advanced, 4=Expert, 5=Master


def find_specialization(db: Session, name: str):
    """Find specialization by name (case-insensitive partial match)"""
    return db.query(Specialization).filter(
        Specialization.name.ilike(f"%{name}%")
    ).first()


def get_or_create_quiz(db: Session, spec_id: int, difficulty: int, spec_name: str):
    """Get existing quiz or create new one"""
    quiz = db.query(Quiz).filter(
        Quiz.specialization_id == spec_id,
        Quiz.difficulty_level == difficulty
    ).first()
    
    if quiz:
        return quiz
    
    quiz = Quiz(
        title=f"{spec_name} - Level {difficulty}",
        description=f"AI-generated assessment for {spec_name}",
        specialization_id=spec_id,
        difficulty_level=difficulty,
        is_active=True,
        time_limit_minutes=30,
        passing_score=70.0
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return quiz


def delete_existing_questions(db: Session, quiz_id: int):
    """Delete all questions and options for a quiz"""
    questions = db.query(Question).filter(Question.quiz_id == quiz_id).all()
    
    for question in questions:
        db.query(QuestionOption).filter(
            QuestionOption.question_id == question.id
        ).delete()
    
    db.query(Question).filter(Question.quiz_id == quiz_id).delete()
    db.commit()


def generate_questions_for_topics(specialization: str, topics: list, difficulty: int, questions_per_topic: int):
    """Generate questions for all topics"""
    all_questions = []
    
    for topic in topics:
        for i in range(questions_per_topic):
            result = generate_quiz_question(
                specialization=specialization,
                topic=topic,
                difficulty=difficulty
            )
            
            if result['success']:
                question_data = result['data']
                question_data['topic'] = topic
                all_questions.append(question_data)
                print(".", end="", flush=True)
            else:
                print("x", end="", flush=True)
    
    print()  # New line after dots
    return all_questions


def insert_questions(db: Session, quiz_id: int, questions: list):
    """Insert questions into database"""
    for idx, q_data in enumerate(questions, 1):
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
        db.flush()
        
        for opt_data in q_data['options']:
            option = QuestionOption(
                question_id=question.id,
                option_text=opt_data['text'],
                is_correct=(opt_data['id'] == q_data['correct_answer']),
                order_index=ord(opt_data['id']) - ord('A')
            )
            db.add(option)
    
    db.commit()


def main():
    """Main execution"""
    print("Generating AI Quiz Questions...")
    print(f"{len(SPECIALIZATIONS_CONFIG)} specializations × {len(DIFFICULTY_LEVELS)} levels\n")
    
    db = SessionLocal()
    
    try:
        total_questions = 0
        
        for spec_name, config in SPECIALIZATIONS_CONFIG.items():
            print(f"\n{spec_name}")
            
            # Find specialization
            spec = find_specialization(db, spec_name)
            if not spec:
                print(f"  Not found in database")
                continue
            
            # Loop through ALL difficulty levels
            for difficulty in DIFFICULTY_LEVELS:
                difficulty_names = {1: "Beginner", 2: "Intermediate", 3: "Advanced", 4: "Expert"}
                print(f"  Level {difficulty} ({difficulty_names.get(difficulty)}): ", end="", flush=True)
                
                try:
                    # Generate questions for this difficulty
                    questions = generate_questions_for_topics(
                        specialization=spec_name,
                        topics=config['topics'],
                        difficulty=difficulty,
                        questions_per_topic=config['questions_per_topic']
                    )
                    
                    if not questions:
                        print("No questions generated")
                        continue
                    
                    # Get or create quiz for this difficulty
                    quiz = get_or_create_quiz(db, spec.id, difficulty, spec.name)
                    
                    # Delete old questions and insert new ones
                    delete_existing_questions(db, quiz.id)
                    insert_questions(db, quiz.id, questions)
                    
                    # Count final questions
                    final_count = db.query(Question).filter(Question.quiz_id == quiz.id).count()
                    print(f" {final_count} questions")
                    
                    total_questions += final_count
                    
                except Exception as e:
                    print(f" Error: {e}")
        
        print(f"\n{'='*50}")
        print(f" Complete: {total_questions} total questions generated")
        print(f"{'='*50}")
        
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
