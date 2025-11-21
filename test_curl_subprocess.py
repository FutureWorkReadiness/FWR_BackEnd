#!/usr/bin/env python3
"""Simple test of curl from Python"""
import subprocess
import json
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

print("Testing curl from Python subprocess...")

payload = {
    "contents": [{"parts": [{"text": "Say hello in one word"}]}]
}

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

curl_cmd = [
    'curl', '-s', '-X', 'POST',
    url,
    '-H', 'Content-Type: application/json',
    '-d', json.dumps(payload)
]

print(f"Running: {' '.join(curl_cmd[:4])}...")

result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=10)

print(f"Return code: {result.returncode}")
print(f"Stdout length: {len(result.stdout)}")
print(f"Stderr: {result.stderr[:200] if result.stderr else 'None'}")

if result.stdout:
    response = json.loads(result.stdout)
    print("\nResponse:")
    print(json.dumps(response, indent=2)[:500])
