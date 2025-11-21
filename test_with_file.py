#!/usr/bin/env python3
"""Test with output to file"""
import subprocess
import json
import os
from dotenv import load_dotenv
import tempfile

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

print("Generating quiz question...")

payload = {
    "contents": [{"parts": [{"text": "What is 2+2? Answer in one word."}]}]
}

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

# Write output to temp file
with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
    output_file = f.name

try:
    # Run curl with output redirected to file
    with open(output_file, 'w') as f:
        result = subprocess.run(
            ['curl', '-s', '-X', 'POST', url,
             '-H', 'Content-Type: application/json',
             '-d', json.dumps(payload)],
            stdout=f,
            stderr=subprocess.PIPE,
            timeout=10
        )
    
    print(f"Return code: {result.returncode}")
    print(f"Stderr: {result.stderr.decode() if result.stderr else 'None'}")
    
    # Read the output file
    with open(output_file, 'r') as f:
        response_text = f.read()
    
    print(f"Response length: {len(response_text)}")
    print(f"Response preview: {response_text[:200]}")
    
    if response_text:
        response = json.loads(response_text)
        text = response['candidates'][0]['content']['parts'][0]['text']
        print(f"\n✅ AI Response: {text}")
    
finally:
    if os.path.exists(output_file):
        os.unlink(output_file)
