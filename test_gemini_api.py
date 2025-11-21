"""
Simple test to verify Gemini API is working
"""
# Fix for Python 3.9 compatibility
import importlib.metadata
if not hasattr(importlib.metadata, 'packages_distributions'):
    def packages_distributions():
        pkg_to_dist = {}
        for dist in importlib.metadata.distributions():
            try:
                dist_name = dist.metadata.get('Name', '')
                for file in (dist.files or []):
                    pkg = file.parts[0] if file.parts else ''
                    if pkg:
                        pkg_to_dist.setdefault(pkg, []).append(dist_name)
            except Exception:
                pass
        return pkg_to_dist
    importlib.metadata.packages_distributions = packages_distributions

import google.generativeai as genai
from google.generativeai import types
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

print(f'API Key: {api_key[:10]}...{api_key[-4:]}' if api_key and len(api_key) > 14 else 'Invalid key')
print('\n1. Testing API connection...')

os.environ['GEMINI_API_KEY'] = api_key
client = genai.Client()
print('✅ Client created')

print('\n2. Testing simple generation (no system instruction)...')
try:
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents="Say hello in one sentence"
    )
    print(f'✅ Response: {response.text}')
except Exception as e:
    print(f'❌ Error: {e}')
    exit(1)

print('\n3. Testing quiz generation...')
try:
    system_instruction = """You are a quiz creator. Generate one multiple-choice question about React Hooks.
Return ONLY valid JSON in this format:
{
    "question": "question text",
    "options": [
        {"id": "A", "text": "option 1"},
        {"id": "B", "text": "option 2"},
        {"id": "C", "text": "option 3"},
        {"id": "D", "text": "option 4"}
    ],
    "correct_answer": "A",
    "explanation": "why A is correct"
}"""

    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents="Generate a beginner-level question about React useState hook.",
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.3,
            max_output_tokens=1024,
        )
    )
    
    print('✅ Quiz generated!')
    text = response.text.strip()
    
    # Clean markdown if present
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    
    text = text.strip()
    quiz_data = json.loads(text)
    print(json.dumps(quiz_data, indent=2))
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
