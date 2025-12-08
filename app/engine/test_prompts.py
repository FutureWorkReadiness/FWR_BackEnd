"""
Simple test to see what Gemini is actually returning
"""
import os
from pathlib import Path
from google import genai

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file in the project root."""
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env_file()

# Initialize client
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise EnvironmentError("GEMINI_API_KEY not set")

client = genai.Client(api_key=api_key)

# Simple test prompt
test_prompt = """
Generate EXACTLY 2 multiple-choice questions for a Frontend Developer interview (Level 1 - Junior).

Output ONLY valid JSON in this exact format:
{
  "quiz_pool": [
    {
      "id": 1,
      "question": "Your question here (12-28 words)",
      "options": [
        {"key": "A", "text": "Option A text", "is_correct": false, "rationale": "Why this is wrong"},
        {"key": "B", "text": "Option B text", "is_correct": true, "rationale": "Why this is correct"},
        {"key": "C", "text": "Option C text", "is_correct": false, "rationale": "Why this is wrong"},
        {"key": "D", "text": "Option D text", "is_correct": false, "rationale": "Why this is wrong"},
        {"key": "E", "text": "Option E text", "is_correct": false, "rationale": "Why this is wrong"}
      ]
    }
  ]
}

Do NOT include any text before or after the JSON. Do NOT use markdown code fences.
"""

print("=" * 80)
print("SENDING REQUEST TO GEMINI...")
print("=" * 80)

try:
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=test_prompt,
        config={
            'temperature': 0.6,
            'response_mime_type': 'application/json'
        }
    )
    
    print("\n" + "=" * 80)
    print("RAW RESPONSE:")
    print("=" * 80)
    print(response.text)
    print("\n" + "=" * 80)
    
    # Try to parse as JSON
    import json
    try:
        parsed = json.loads(response.text)
        print("✓ JSON PARSING SUCCESSFUL!")
        print("\nParsed data:")
        print(json.dumps(parsed, indent=2))
    except json.JSONDecodeError as e:
        print(f"✗ JSON PARSING FAILED: {e}")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
