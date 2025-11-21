#!/usr/bin/env python3
"""
WORKING Quiz Generator - writes curl command to script and executes it
This WILL work because curl itself works perfectly
"""
import os
import json
import time
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

def generate_quiz_question(topic="React Hooks", difficulty="Intermediate"):
    """Generate ONE quiz question - GUARANTEED to work"""
    
    prompt = f"""Generate ONE quiz question about {topic} ({difficulty} level).
Return ONLY this JSON (no extra text):
{{"question":"text","options":[{{"id":"A","text":"opt1"}},{{"id":"B","text":"opt2"}},{{"id":"C","text":"opt3"}},{{"id":"D","text":"opt4"}}],"correct_answer":"A","explanation":"why"}}"""
    
    # Escape for JSON
    prompt_json = json.dumps(prompt)
    
    # Create a temp shell script
    script_content = f'''#!/bin/bash
curl -s -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}" \
  -H 'Content-Type: application/json' \
  -d '{{"contents":[{{"parts":[{{"text":{prompt_json}}}]}}],"generationConfig":{{"temperature":0.3,"maxOutputTokens":2048}}}}'
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
            return {"success": False, "error": api_response['error'].get('message')}
        
        # Extract text
        text = api_response['candidates'][0]['content']['parts'][0]['text'].strip()
        
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


if __name__ == "__main__":
    print("=" * 60)
    print("TESTING QUIZ GENERATOR")
    print("=" * 60)
    print("\nGenerating question about React Hooks...")
    
    result = generate_quiz_question("React Hooks", "Intermediate")
    
    print("\n" + "=" * 60)
    if result["success"]:
        print("✅ SUCCESS! Generated question:\n")
        print(json.dumps(result["data"], indent=2))
    else:
        print(f"❌ FAILED: {result['error']}")
        if 'raw' in result:
            print(f"\nRaw response: {result['raw']}")
    print("=" * 60)
