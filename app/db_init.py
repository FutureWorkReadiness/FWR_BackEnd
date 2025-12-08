"""
Automatic database initialization - populates data if database is empty
This runs automatically when the app starts
Loads data from the `SECTOR_TRACKS` config in `app/engine/prompts.py`
"""
import os
from pathlib import Path
from .database import SessionLocal
from .models.models_hierarchical import Sector, Branch, Specialization, Quiz, Question, QuestionOption
import json

# Import SECTOR_TRACKS to use it as the source of truth
from .engine.prompts import SECTOR_TRACKS

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Load initial data from JSON files
def load_sectors_from_json():
    """Loads sector data from the embedded JSON file."""
    sectors_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'sectors.json')
    with open(sectors_file, 'r') as f:
        return json.load(f)

def load_quizzes_from_json():
    """Load quizzes data from JSON file"""
    quizzes_file = DATA_DIR / "quizzes.json"
    if not quizzes_file.exists():
        print(f"⚠️  Quizzes JSON file not found at {quizzes_file}")
        return None
    
    with open(quizzes_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get("quizzes", [])

def auto_populate_if_empty():
    """
    Automatically populate database with required data if tables are empty
    Loads data from JSON files in the data/ directory
    This ensures the app always has basic data to work with
    """
    db = SessionLocal()
    try:
        # Check if any sectors exist
        sector_count = db.query(Sector).count()
        
        # We will now use SECTOR_TRACKS as the source of truth.
        # This logic will add any missing sectors, branches, or specializations.
        print("📊 Verifying database structure against `SECTOR_TRACKS`...")
        
        added_items = 0
        
        # Process each sector from the SECTOR_TRACKS dictionary
        for sector_name, specializations_list in SECTOR_TRACKS.items():
            # Format sector name (e.g., "health_social_care" -> "Health Social Care")
            formatted_sector_name = sector_name.replace('_', ' ').title()
            
            # Find or create the Sector
            sector = db.query(Sector).filter(Sector.name == formatted_sector_name).first()
            if not sector:
                sector = Sector(name=formatted_sector_name, description=f"{formatted_sector_name} sector")
                db.add(sector)
                db.commit()
                db.refresh(sector)
                print(f"✅ Created sector: {sector.name}")
                added_items += 1
            
            # Create a default "General" branch for this sector if it doesn't exist
            branch_name = f"{formatted_sector_name} General"
            branch = db.query(Branch).filter(Branch.name == branch_name, Branch.sector_id == sector.id).first()
            if not branch:
                branch = Branch(name=branch_name, description=f"General branch for {formatted_sector_name}", sector_id=sector.id)
                db.add(branch)
                db.commit()
                db.refresh(branch)
                print(f"  ✅ Created branch: {branch.name}")
                added_items += 1
            
            # Process specializations (careers) for this branch
            for spec_name in specializations_list:
                formatted_spec_name = spec_name.replace('_', ' ').title()
                specialization = db.query(Specialization).filter(Specialization.name == formatted_spec_name, Specialization.branch_id == branch.id).first()
                if not specialization:
                    specialization = Specialization(name=formatted_spec_name, description=f"{formatted_spec_name} role", branch_id=branch.id)
                    db.add(specialization)
                    added_items += 1
                    print(f"    ✅ Added specialization: {specialization.name}")
        
        if added_items > 0:
            db.commit()
            print(f"✅ Structure sync complete. Added {added_items} new items.")
        else:
            print("✅ Database structure is already in sync with `SECTOR_TRACKS`.")
            
        # --- Quiz Population Logic (from JSON files) ---
        # This part remains unchanged to allow loading quizzes from data/quizzes.json
        quiz_count = db.query(Quiz).count()
        quizzes_data = load_quizzes_from_json()
        
        if quizzes_data:
            added_count = 0
            for quiz_data in quizzes_data:
                # Find specialization by formatted name
                formatted_spec_name = quiz_data["specialization"].replace('_', ' ').title()
                specialization = db.query(Specialization).filter(
                    Specialization.name == formatted_spec_name
                ).first()
                
                if not specialization:
                    print(f"⚠️  Specialization '{formatted_spec_name}' not found. Skipping quiz: {quiz_data['title']}")
                    continue
                
                existing_quiz = db.query(Quiz).filter(
                    Quiz.title == quiz_data["title"],
                    Quiz.specialization_id == specialization.id
                ).first()
                
                if not existing_quiz:
                    # Create missing quiz
                    quiz = Quiz(
                        title=quiz_data["title"],
                        description=quiz_data["description"],
                        specialization_id=specialization.id,
                        difficulty_level=quiz_data["difficulty_level"],
                        time_limit_minutes=quiz_data["time_limit_minutes"],
                        passing_score=quiz_data["passing_score"]
                    )
                    db.add(quiz)
                    db.commit()
                    db.refresh(quiz)
                    
                    # Add questions
                    for idx, q_data in enumerate(quiz_data.get("questions", [])):
                        question = Question(
                            quiz_id=quiz.id,
                            question_text=q_data["question_text"],
                            question_type=q_data["question_type"],
                            points=q_data.get("points", 1),
                            order_index=idx + 1,
                            explanation=q_data.get("explanation")
                        )
                        db.add(question)
                        db.flush()
                        
                        for opt_idx, option_data in enumerate(q_data.get("options", [])):
                            option = QuestionOption(
                                question_id=question.id,
                                option_text=option_data["text"],
                                is_correct=option_data["is_correct"],
                                order_index=opt_idx + 1
                            )
                            db.add(option)
                    
                    db.commit()
                    added_count += 1
                    print(f"📝 Added new quiz: {quiz.title}")
            
            if added_count > 0:
                print(f"📝 Added {added_count} new quiz(zes) from JSON files.")
            else:
                print(f"✅ Quizzes are already up-to-date.")
        else:
            if quiz_count == 0:
                print("⚠️  Could not load quizzes from JSON file.")
            else:
                print(f"✅ Database already populated with {quiz_count} quizzes.")

        print("✅ Auto-population check complete!")
                    
    except Exception as e:
        print(f"⚠️  Auto-population error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()
