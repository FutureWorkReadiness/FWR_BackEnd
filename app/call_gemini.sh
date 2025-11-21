#!/bin/bash
# Simple script to call Gemini API
# Usage: ./call_gemini.sh "your prompt here"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../.env"

PROMPT="$1"

curl -s -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${GEMINI_API_KEY}" \
  -H 'Content-Type: application/json' \
  -d "{\"contents\":[{\"parts\":[{\"text\":\"${PROMPT}\"}]}],\"generationConfig\":{\"temperature\":0.3,\"maxOutputTokens\":1024}}"
