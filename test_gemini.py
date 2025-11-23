"""
Test Gemini API and list available models
"""



#----------new prompt code --------------------

import google.generativeai as genai
from google.generativeai import types
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

os.environ['GEMINI_API_KEY'] = api_key
client = genai.Client()

# Define the list of topics you want to generate quizzes for
topics = [
    "Frontend Development",
    "Data Science",
    "Cybersecurity Analyst",
]

# Define the 5 levels of difficulty
difficulties = ["Novice", "Beginner", "Intermediate", "Advanced", "Expert"]

print('\nStarting quiz generation for multiple topics and difficulties...')

# Outer loop for each topic
for topic in topics:
    # Inner loop for each difficulty level
    for difficulty in difficulties:
        try:
            # The system instruction can remain general, with the content prompt being specific
            system_instruction = f"""You are an expert quiz creator. Generate one multiple-choice question about the specific topic and difficulty provided.
The question should be suitable for a person at the **{difficulty}** level.
Return ONLY valid JSON in this format:
{{
    "question": "question text",
    "options": [
        {{"id": "A", "text": "option 1"}},
        {{"id": "B", "text": "option 2"}},
        {{"id": "C", "text": "option 3"}},
        {{"id": "D", "text": "option 4"}}
    ],
    "correct_answer": "A",
    "explanation": "why A is correct"
}}"""

            # The specific content prompt changes with each iteration
            content_prompt = f"Generate one question about: {topic}."

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=content_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.3,
                    max_output_tokens=1024,
                )
            )
            
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

            print(f'\n--- Quiz for Topic: **{topic}**, Difficulty: **{difficulty}** ---')
            print(json.dumps(quiz_data, indent=2))
            
        except Exception as e:
            print(f'Error generating quiz for topic "{topic}" at difficulty "{difficulty}": {e}')

print('\nAll quizzes generated or attempted.')




# old prompt code -------


# import google.generativeai as genai
# import os
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Configure Gemini
# api_key = os.getenv("GEMINI_API_KEY")
# print(f"API Key loaded: {api_key[:10]}..." if api_key else "❌ No API key found")

# genai.configure(api_key=api_key)

# print("\n" + "=" * 60)
# print("LISTING AVAILABLE MODELS")
# print("=" * 60)

# try:
#     for model in genai.list_models():
#         if 'generateContent' in model.supported_generation_methods:
#             print(f"✅ {model.name}")
#             print(f"   Display name: {model.display_name}")
#             print(f"   Description: {model.description[:100]}...")
#             print()
# except Exception as e:
#     print(f" Error listing models: {e}")

# print("\n" + "=" * 60)
# print("TESTING SIMPLE GENERATION")
# print("=" * 60)

# # Try with the most common model names
# model_names_to_try = [
#     "gemini-pro",
#     "gemini-1.5-pro",
#     "gemini-1.5-flash",
#     "models/gemini-pro",
#     "models/gemini-1.5-pro"
# ]

# for model_name in model_names_to_try:
#     try:
#         print(f"\nTrying model: {model_name}...", end=" ")
#         model = genai.GenerativeModel(model_name)
#         response = model.generate_content("Say 'Hello' in JSON format: {\"message\": \"Hello\"}")
#         print("✅ SUCCESS!")
#         print(f"Response: {response.text[:100]}")
#         break
#     except Exception as e:
#         print(f"❌ {str(e)[:80]}")
