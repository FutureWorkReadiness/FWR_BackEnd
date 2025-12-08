
import json
import glob
import random
import re
from collections import defaultdict
# --- Configuration ---

# Use glob to find all relevant JSON files in the context.
# This makes it easy to add new files without changing the script.
JSON_FILES = [
    "/home/hiba/Desktop/FWR_BackEnd/app/outputs/clean_quiz_chunks_gemini_v3/technology_FRONTEND_DEVELOPER_lvl1_critic_attempt1.json",
    "/home/hiba/Desktop/FWR_BackEnd/app/outputs/clean_quiz_chunks_gemini_v3/technology_DATA_SCIENTIST_lvl3_critic_attempt1.json",
    "/home/hiba/Desktop/FWR_BackEnd/app/outputs/clean_quiz_chunks_gemini_v3/technology_DATA_SCIENTIST_lvl4_critic_attempt1.json",
    # Add other file paths from context if they exist and are needed.
    # For example:
    # "/home/hiba/Desktop/FWR_BackEnd/app/outputs/raw_responses_gemini_v3/critic:technology_DATA_SCIENTIST_lvl3_critic_attempt1_attempt1.txt",
    # ... and so on for all provided files.
]

CAREERS_TO_AUDIT = ["DATA_SCIENTIST", "FRONTEND_DEVELOPER"]

# --- Utility Functions ---

def normalize_question_text(text):
    """
    Normalizes question text for accurate duplicate detection.
    Converts to lowercase, removes punctuation and extra whitespace.
    """
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def load_all_questions(files):
    """Loads all questions from a list of JSON files."""
    all_questions = []
    for file_path in files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                for question in data.get("quiz_pool", []):
                    question['source_file'] = file_path
                    all_questions.append(question)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Warning: Could not process file {file_path}. Error: {e}")
    return all_questions

# --- Critic Simulation ---

def call_semantic_critic(question_text):
    """
    Simulates the 'Semantic Critic' based on Bloom's Taxonomy proxy.
    This is a placeholder for the actual Gemini 2.5 Pro model call.
    """
    # Simple keyword-based logic for simulation
    higher_order_keywords = ['why', 'how does', 'what is the advantage', 'compare', 'contrast', 'design', 'optimize', 'best balances', 'most robust']
    question_lower = question_text.lower()
    if any(keyword in question_lower for keyword in higher_order_keywords):
        return 'HIGHER_ORDER'
    return 'LOWER_ORDER'

def call_super_critic(question_obj):
    """
    Simulates the 'Super-Critic' for hallucination and relevance.
    This is a placeholder for the actual Gemini 2.5 Pro model call.
    """
    # In a real scenario, this would make an API call.
    # For simulation, we'll pass all questions. A real implementation
    # would have logic to sometimes fail questions.
    return 1, "Pass: The concepts and tools mentioned are industry-standard."

# --- Audit Functions ---

def perform_deduplication_audit(questions):
    """2.1 Cross-Board Deduplication Audit"""
    print("\n--- 2.1 Cross-Board Deduplication Audit ---")
    total_questions = len(questions)
    normalized_questions_set = {normalize_question_text(q['question']) for q in questions}
    unique_questions = len(normalized_questions_set)

    print(f"Total questions extracted: {total_questions}")
    print(f"Unique questions found: {unique_questions}")

    if total_questions == unique_questions:
        print("Global Uniqueness Check: PASS\n")
    else:
        print(f"Global Uniqueness Check: FAIL ({total_questions - unique_questions} duplicates found)\n")

def perform_level_flow_audit(all_questions):
    """2.2 Level of Intensity Flow (Semantic Scoring)"""
    print("\n--- 2.2 Level of Intensity Flow Audit ---")
    
    # Group questions by career and level
    questions_by_career_level = defaultdict(list)
    for q in all_questions:
        # Extract career and level from filename, e.g., 'technology_DATA_SCIENTIST_lvl3_...'
        match = re.search(r'technology_([A-Z_]+)_lvl(\d+)', q['source_file'])
        if match:
            career, level = match.groups()
            questions_by_career_level[(career, int(level))].append(q)

    for (career, level), questions in sorted(questions_by_career_level.items()):
        if not questions:
            continue
        
        # Sample up to 3 questions
        sample_size = min(3, len(questions))
        sampled_questions = random.sample(questions, sample_size)
        
        higher_order_count = 0
        for q in sampled_questions:
            score = call_semantic_critic(q['question'])
            if score == 'HIGHER_ORDER':
                higher_order_count += 1
        
        percentage_higher = (higher_order_count / sample_size) * 100
        print(f"Career: {career}, Level: {level}")
        print(f"  - Sampled {sample_size} questions.")
        print(f"  - HIGHER_ORDER percentage: {percentage_higher:.2f}%")

    print("\nAudit Check: Manually verify that HIGHER_ORDER percentage increases with level.")
    print("For example, L4 should have a higher percentage than L3 for the same career.\n")


def perform_hallucination_audit(all_questions):
    """3.1 Hallucination and Relevance Audit"""
    print("\n--- 3.1 Hallucination and Relevance Audit ---")
    
    questions_by_career = defaultdict(list)
    for q in all_questions:
        match = re.search(r'technology_([A-Z_]+)_lvl(\d+)', q['source_file'])
        if match:
            career, _ = match.groups()
            questions_by_career[career].append(q)

    failed_questions = []
    for career, questions in questions_by_career.items():
        if not questions:
            continue
        
        # Sample 10 questions per career
        sample_size = min(10, len(questions))
        sampled_questions = random.sample(questions, sample_size)
        
        print(f"\nAuditing career: {career} (sampled {sample_size} questions)")
        
        for q in sampled_questions:
            score, explanation = call_super_critic(q)
            if score == 0:
                failed_questions.append((q, explanation))
                print(f"  - FAIL: Question ID {q.get('id', 'N/A')}")
            else:
                print(f"  - PASS: Question ID {q.get('id', 'N/A')}")

    if not failed_questions:
        print("\nSuper-Critic Audit Result: PASS. No hallucinations or relevance issues found in sample.")
    else:
        print(f"\nSuper-Critic Audit Result: FAIL. Found {len(failed_questions)} potential issues.")
        for q, explanation in failed_questions:
            print(f"\n  - Question ID: {q.get('id', 'N/A')} from {q['source_file']}")
            print(f"    Question: {q['question']}")
            print(f"    Reason: {explanation}")
        print("\nAction: Manually review failed questions and consider generator prompt tuning.")


if __name__ == "__main__":
    print("Starting Automated Quality Verification Script...")
    
    all_questions_data = load_all_questions(JSON_FILES)
    
    if not all_questions_data:
        print("No questions found to audit. Exiting.")
    else:
        perform_deduplication_audit(all_questions_data)
        perform_level_flow_audit(all_questions_data)
        perform_hallucination_audit(all_questions_data)

    print("\nScript finished.")