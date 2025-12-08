#!/usr/bin/env python3
"""
Simple test to generate a single quiz and debug the output
"""
import os
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

# Load .env
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

# Now import and run
from engine.prompts import GeminiQuizGeneratorV3

print("=" * 80)
print("Testing single quiz generation")
print("=" * 80)

generator = GeminiQuizGeneratorV3()

# Generate just one quiz
sector = "technology"
career = "FRONTEND_DEVELOPER"
level = 1

print(f"\nGenerating: {sector} / {career} / Level {level}")
print("-" * 80)

result = generator.generate_raw_quiz(sector, career, level)

if result:
    print("\n✅ SUCCESS! Generated quiz")
    print(f"Number of questions: {len(result.get('quiz_pool', []))}")
    
    # Save to a test file
    import json
    output_file = Path(__file__).parent / "app" / "outputs" / "test_single_quiz.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved to: {output_file}")
else:
    print("\n❌ FAILED to generate quiz")
    print("Check the raw response files in app/outputs/raw_responses_gemini_v3/")

print("\n" + "=" * 80)
