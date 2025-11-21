import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

print(f"API Key: {API_KEY[:10]}...{API_KEY[-4:]}")

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

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

payload = {
    "contents": [{
        "parts": [{
            "text": "Generate a beginner-level question about React useState hook."
        }]
    }],
    "systemInstruction": {
        "parts": [{
            "text": system_instruction
        }]
    },
    "generationConfig": {
        "temperature": 0.3,
        "maxOutputTokens": 1024,
    }
}

print("\nSending request...")
response = requests.post(url, json=payload, timeout=30)
print(f"Status: {response.status_code}")

result = response.json()
print("\nResponse:")
print(json.dumps(result, indent=2))
