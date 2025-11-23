"""
Test Gemini API and list available models
"""
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key loaded: {api_key[:10]}..." if api_key else "❌ No API key found")

genai.configure(api_key=api_key)

print("\n" + "=" * 60)
print("LISTING AVAILABLE MODELS")
print("=" * 60)

try:
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"✅ {model.name}")
            print(f"   Display name: {model.display_name}")
            print(f"   Description: {model.description[:100]}...")
            print()
except Exception as e:
    print(f" Error listing models: {e}")

print("\n" + "=" * 60)
print("TESTING SIMPLE GENERATION")
print("=" * 60)

# Try with the most common model names
model_names_to_try = [
    "gemini-pro",
    "gemini-1.5-pro",
    "gemini-1.5-flash",
    "models/gemini-pro",
    "models/gemini-1.5-pro"
]

for model_name in model_names_to_try:
    try:
        print(f"\nTrying model: {model_name}...", end=" ")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say 'Hello' in JSON format: {\"message\": \"Hello\"}")
        print("✅ SUCCESS!")
        print(f"Response: {response.text[:100]}")
        break
    except Exception as e:
        print(f"❌ {str(e)[:80]}")
