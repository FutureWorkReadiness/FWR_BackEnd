"""
STRONG MINI TEST SUITE (QA + Relevance + Duplicates)
For evaluating Gemini-generated career interview questions.

This performs:
1. Industry Relevance Analysis
2. Semantic Duplicate Detection
3. Quality Assessment (clarity, realism, correctness)
4. Final consolidated test report
"""

import os
import sys
import json
from typing import List, Dict, Any
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from engine.prompts import GeminiQuizGeneratorV3, ensure_dirs, load_env_file
from google import genai
from google.genai import types

# Load environment variables
load_env_file()

MODEL_EVAL = "gemini-2.0-flash-exp"   # Model for evaluation


# -------------------------
# Utility
# -------------------------

def call_gemini_eval(prompt: str):
    """Call Gemini for evaluation."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found in environment")
        return None
        
    client = genai.Client(api_key=api_key)

    try:
        response = client.models.generate_content(
            model=MODEL_EVAL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="You are a strict QA evaluator for interview questions.",
                temperature=0.1,
                response_mime_type="application/json"
            ),
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Evaluation error: {e}")
        return None


# -------------------------
# 1) Relevance Evaluation
# -------------------------

def evaluate_relevance(question: dict, career: str, level: int) -> dict:
    """Ask Gemini if the question is industry-relevant."""
    q_text = question["question"]

    prompt = f"""
Evaluate the following interview question for the role: {career}.
Level: {level}

QUESTION:
"{q_text}"

Rate the following from 1 to 5 and return ONLY JSON:

{{
  "relevance_score": 5,
  "reason": "explanation here",
  "is_hallucinated": false,
  "hallucination_reason": ""
}}

Rules:
- relevance_score: 1 = irrelevant, 5 = strong relevance to real industry interview
- is_hallucinated = true if the question mentions non-existent tools, laws, models, or unrealistic tasks.
"""

    result = call_gemini_eval(prompt)
    return result or {
        "relevance_score": 0,
        "reason": "Model failed",
        "is_hallucinated": True,
        "hallucination_reason": "Parsing error"
    }


# -------------------------
# 2) Duplicate Analysis
# -------------------------

def detect_semantic_duplicate(q1: str, q2: str) -> bool:
    """Ask Gemini whether q1 and q2 are semantically duplicate."""
    prompt = f"""
Are these two questions semantically the same? Return ONLY JSON.

Q1: "{q1}"
Q2: "{q2}"

Return:
{{
  "duplicate": false,
  "reason": "explanation"
}}
"""
    result = call_gemini_eval(prompt)
    if result:
        return result.get("duplicate", False)
    return False


def duplicate_report(questions: List[dict]) -> List[dict]:
    """Check each pair for semantic duplicates."""
    duplicates = []
    n = len(questions)

    print(f"Checking {n * (n-1) // 2} question pairs for duplicates...")
    
    for i in range(n):
        for j in range(i + 1, n):
            print(f"  Comparing Q{i+1} vs Q{j+1}...", end="\r")
            if detect_semantic_duplicate(questions[i]["question"], questions[j]["question"]):
                duplicates.append({
                    "q1_id": questions[i]["id"],
                    "q1": questions[i]["question"],
                    "q2_id": questions[j]["id"],
                    "q2": questions[j]["question"]
                })
    
    print()  # New line after progress
    return duplicates


# -------------------------
# 3) Quality Evaluation
# -------------------------

def evaluate_quality(question: dict) -> dict:
    """Checks clarity, correctness, distractors, difficulty."""
    prompt = f"""
Evaluate the overall quality of this multiple-choice interview question:

QUESTION:
{json.dumps(question, indent=2)}

Return ONLY JSON:
{{
  "clarity": 5,
  "difficulty": 3,
  "correctness": 5,
  "realism": 5,
  "overall_quality": 5,
  "notes": "detailed feedback"
}}

Rules:
- clarity: 1 unclear, 5 crystal clear
- difficulty: 1 too easy, 5 appropriately challenging
- correctness: 1 incorrect/ambiguous, 5 correct and verifiable
- realism: 1 unrealistic, 5 realistic for actual job interview
- overall_quality: holistic evaluation 1–5
"""
    result = call_gemini_eval(prompt)
    return result or {
        "clarity": 0,
        "difficulty": 0,
        "correctness": 0,
        "realism": 0,
        "overall_quality": 0,
        "notes": "Model failed"
    }


# -------------------------
# FULL MINI TEST RUN
# -------------------------

def run_strong_test():
    """Run comprehensive test suite."""
    ensure_dirs()
    gen = GeminiQuizGeneratorV3()

    SECTOR = "technology"
    CAREER = "FRONTEND_DEVELOPER"
    LEVELS = [1, 2]  # Start with just 2 levels for faster testing

    print("\n" + "="*60)
    print("     STRONG MINI TEST SUITE STARTED")
    print("="*60 + "\n")
    print(f"Sector: {SECTOR}")
    print(f"Career: {CAREER}")
    print(f"Levels: {LEVELS}\n")

    # ---- Step 1: Generate questions ----
    all_questions = []

    for level in LEVELS:
        print(f"\n{'='*60}")
        print(f"  GENERATING LEVEL {level}")
        print('='*60)

        # generate_for_career_level writes results into gen.results_bank
        gen.generate_for_career_level(SECTOR, CAREER, level)

        # Collect from the generator's results_bank
        block = gen.results_bank.get(SECTOR, {}).get(CAREER, {}).get(f"level_{level}", {})
        level_questions = block.get("quiz_pool", [])
        if level_questions:
            print(f"✅ Generated {len(level_questions)} questions for Level {level}")
            for q in level_questions:
                q["level"] = level
                all_questions.append(q)
        else:
            print(f"❌ Failed to generate questions for Level {level}")

    if not all_questions:
        print("\n❌ No questions generated. Test aborted.")
        return

    print(f"\n{'='*60}")
    print(f"  COLLECTED {len(all_questions)} TOTAL QUESTIONS")
    print('='*60 + "\n")

    # ---- Step 2: Relevance Evaluation ----
    print(f"\n{'='*60}")
    print("  STEP 2: RELEVANCE EVALUATION")
    print('='*60)
    
    relevance_scores = []
    for idx, q in enumerate(all_questions, 1):
        print(f"\n[{idx}/{len(all_questions)}] Evaluating relevance (Level {q['level']}, Q{q['id']})...")
        evaluation = evaluate_relevance(q, CAREER, q["level"])
        relevance_scores.append({
            "question_id": q["id"],
            "question": q["question"],
            "level": q["level"],
            "evaluation": evaluation
        })
        print(f"   Score: {evaluation.get('relevance_score', 0)}/5")

    # ---- Step 3: Duplicate Check ----
    print(f"\n{'='*60}")
    print("  STEP 3: DUPLICATE DETECTION")
    print('='*60 + "\n")
    
    duplicates = duplicate_report(all_questions)
    
    if duplicates:
        print(f"\n⚠️  Found {len(duplicates)} duplicate(s)")
        for dup in duplicates:
            print(f"   - Q{dup['q1_id']} ≈ Q{dup['q2_id']}")
    else:
        print("✅ No duplicates found")

    # ---- Step 4: Quality Evaluation ----
    print(f"\n{'='*60}")
    print("  STEP 4: QUALITY EVALUATION")
    print('='*60)
    
    quality_scores = []
    for idx, q in enumerate(all_questions, 1):
        print(f"\n[{idx}/{len(all_questions)}] Evaluating quality (Level {q['level']}, Q{q['id']})...")
        evaluation = evaluate_quality(q)
        quality_scores.append({
            "question_id": q["id"],
            "question": q["question"],
            "level": q["level"],
            "evaluation": evaluation
        })
        print(f"   Overall Quality: {evaluation.get('overall_quality', 0)}/5")

    # ---- Calculate Statistics ----
    avg_relevance = sum(r["evaluation"].get("relevance_score", 0) for r in relevance_scores) / len(relevance_scores) if relevance_scores else 0
    avg_quality = sum(q["evaluation"].get("overall_quality", 0) for q in quality_scores) / len(quality_scores) if quality_scores else 0
    hallucinated_count = sum(1 for r in relevance_scores if r["evaluation"].get("is_hallucinated", False))

    # ---- Save Full Report ----
    report = {
        "test_metadata": {
            "career": CAREER,
            "sector": SECTOR,
            "levels_tested": LEVELS,
            "total_questions": len(all_questions),
            "date": "2025-11-30"
        },
        "summary_statistics": {
            "average_relevance_score": round(avg_relevance, 2),
            "average_quality_score": round(avg_quality, 2),
            "hallucinated_questions": hallucinated_count,
            "duplicate_pairs": len(duplicates)
        },
        "relevance_analysis": relevance_scores,
        "duplicates_found": duplicates,
        "quality_analysis": quality_scores,
    }

    output_file = "strong_test_report.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # ---- Print Summary ----
    print("\n" + "="*60)
    print("  TEST SUITE COMPLETE")
    print("="*60)
    print(f"\n📊 SUMMARY:")
    print(f"   Total Questions: {len(all_questions)}")
    print(f"   Avg Relevance: {avg_relevance:.2f}/5")
    print(f"   Avg Quality: {avg_quality:.2f}/5")
    print(f"   Hallucinated: {hallucinated_count}")
    print(f"   Duplicates: {len(duplicates)}")
    print(f"\n✅ Report saved to: {output_file}")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_strong_test()
