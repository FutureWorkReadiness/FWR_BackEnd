#!/bin/bash
# Helper script to call Gemini API
# Usage: quiz_api_call.sh "your prompt text"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../.env"

PROMPT="$1"

# Call Gemini API
curl -s -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${GEMINI_API_KEY}" \
  -H 'Content-Type: application/json' \
  --data-raw "{\"contents\":[{\"parts\":[{\"text\":$(echo "$PROMPT" | python3 -c 'import sys, json; print(json.dumps(sys.stdin.read()))')}]}],\"generationConfig\":{\"temperature\":0.3,\"maxOutputTokens\":1024}}"
