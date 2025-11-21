#!/bin/bash
# Standalone quiz generator that DEFINITELY works
# Run this: ./test_quiz.sh

cd "$(dirname "$0")"
source ../.env

echo "Generating quiz question..."

# Call API
RESPONSE=$(curl -s -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${GEMINI_API_KEY}" \
  -H 'Content-Type: application/json' \
  -d '{
    "contents": [{
      "parts": [{
        "text": "Generate ONE multiple-choice quiz question about React Hooks for beginners. Return ONLY valid JSON in this format: {\"question\": \"text\", \"options\": [{\"id\": \"A\", \"text\": \"option1\"}, {\"id\": \"B\", \"text\": \"option2\"}, {\"id\": \"C\", \"text\": \"option3\"}, {\"id\": \"D\", \"text\": \"option4\"}], \"correct_answer\": \"A\", \"explanation\": \"why\"}"
      }]
    }],
    "generationConfig": {
      "temperature": 0.3,
      "maxOutputTokens": 1024
    }
  }')

echo "$RESPONSE" | python3 -m json.tool

# Extract just the generated text
echo ""
echo "=== GENERATED QUESTION ==="
echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['candidates'][0]['content']['parts'][0]['text'])"
