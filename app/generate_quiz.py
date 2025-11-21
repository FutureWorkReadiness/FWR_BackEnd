#!/usr/bin/env python3
"""
Quiz Generator for Future of Work Platform
Uses Gemini 2.5 Flash API to generate quiz questions
"""
import os
import json
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

def generate_quiz_question(
    specialization: str,
    topic: str,
    difficulty: int = 3,
    num_options: int = 4
):
    """
    Generate ONE quiz question using Gemini AI
    
    Args:
        specialization: e.g., "Frontend Development", "Data Science"
        topic: e.g., "React Hooks", "Machine Learning"
        difficulty: 1-5 (1=Beginner, 5=Expert)
        num_options: Number of answer options (default 4)
    
    Returns:
        dict with success status and question data
    """
    
    difficulty_map = {
        1: "Beginner",
        2: "Intermediate",
        3: "Advanced",
        4: "Expert",
        5: "Master"
    }
    
    difficulty_level = difficulty_map.get(difficulty, "Intermediate")
    
    # Ultra-concise prompt to minimize token usage
    prompt = f"""Quiz: {topic} ({difficulty_level}).
JSON only:
{{"question":"...","options":[{{"id":"A","text":"..."}},{{"id":"B","text":"..."}},{{"id":"C","text":"..."}},{{"id":"D","text":"..."}}],"correct_answer":"A","explanation":"..."}}"""
    
    # Escape for JSON
    prompt_json = json.dumps(prompt)
    
    # Create a temp shell script with increased token limit
    script_content = f'''#!/bin/bash
curl -s -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}" \
  -H 'Content-Type: application/json' \
  -d '{{"contents":[{{"parts":[{{"text":{prompt_json}}}]}}],"generationConfig":{{"temperature":0.3,"maxOutputTokens":4096}}}}'
'''
    
    script_file = "/tmp/quiz_gen.sh"
    output_file = "/tmp/quiz_response.json"
    
    # Write script
    with open(script_file, 'w') as f:
        f.write(script_content)
    os.chmod(script_file, 0o755)
    
    # Execute and capture output
    os.system(f"{script_file} > {output_file} 2>&1")
    
    try:
        # Read response
        with open(output_file, 'r') as f:
            api_response = json.load(f)
        
        if 'error' in api_response:
            return {"success": False, "error": api_response['error'].get('message', 'API error')}
        
        # Check if response has candidates
        if 'candidates' not in api_response or len(api_response['candidates']) == 0:
            return {"success": False, "error": "No candidates in response"}
        
        candidate = api_response['candidates'][0]
        
        # Check finish reason
        finish_reason = candidate.get('finishReason', '')
        if finish_reason == 'MAX_TOKENS':
            return {"success": False, "error": "Response too long (MAX_TOKENS exceeded)"}
        
        # Check if we have content and parts
        if 'content' not in candidate:
            return {"success": False, "error": "No content in response"}
        
        if 'parts' not in candidate['content'] or len(candidate['content']['parts']) == 0:
            return {"success": False, "error": f"No parts in content (finish: {finish_reason})"}
        
        # Extract text
        text = candidate['content']['parts'][0]['text'].strip()
        
        # Clean markdown
        for marker in ['```json', '```']:
            if text.startswith(marker):
                text = text[len(marker):]
        if text.endswith('```'):
            text = text[:-3]
        text = text.strip()
        
        # Parse question
        question_data = json.loads(text)
        
        return {"success": True, "data": question_data}
        
    except Exception as e:
        # Read raw response for debugging
        try:
            with open(output_file, 'r') as f:
                raw = f.read()
            return {"success": False, "error": str(e), "raw": raw[:500]}
        except:
            return {"success": False, "error": str(e)}


def generate_full_quiz(
    specialization: str,
    topics: list,
    questions_per_topic: int = 2,
    difficulty: int = 3
):
    """
    Generate a complete quiz with multiple questions
    
    Args:
        specialization: e.g., "Frontend Development"
        topics: List of topics, e.g., ["React Hooks", "State Management"]
        questions_per_topic: How many questions per topic
        difficulty: 1-5
    
    Returns:
        List of generated questions
    """
    all_questions = []
    
    for topic in topics:
        print(f"\n📝 Generating {questions_per_topic} questions for: {topic}")
        
        for i in range(questions_per_topic):
            print(f"   Question {i+1}/{questions_per_topic}...", end=" ", flush=True)
            
            result = generate_quiz_question(
                specialization=specialization,
                topic=topic,
                difficulty=difficulty
            )
            
            if result["success"]:
                all_questions.append({
                    "topic": topic,
                    "difficulty": difficulty,
                    **result["data"]
                })
                print("✅")
            else:
                print(f"❌ {result['error']}")
    
    return all_questions


if __name__ == "__main__":
    print("=" * 60)
    print("QUIZ GENERATOR - Frontend Development")
    print("=" * 60)
    
    # Generate a full quiz
    quiz = generate_full_quiz(
        specialization="Frontend Development",
        topics=[
            "React Hooks",
            "State Management",
            "Component Lifecycle"
        ],
        questions_per_topic=2,
        difficulty=3
    )
    
    print(f"\n✅ Generated {len(quiz)} questions total!\n")
    
    if len(quiz) > 0:
        print("=" * 60)
        print("SAMPLE QUESTION:")
        print("=" * 60)
        print(json.dumps(quiz[0], indent=2))
        print("\n" + "=" * 60)
        print(f"All {len(quiz)} questions ready!")
        print("=" * 60)
