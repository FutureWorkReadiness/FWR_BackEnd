"""
Quick test with different model names
"""
# Fix for Python 3.9
import importlib.metadata
if not hasattr(importlib.metadata, 'packages_distributions'):
    def packages_distributions():
        pkg_to_dist = {}
        for dist in importlib.metadata.distributions():
            try:
                dist_name = dist.metadata.get('Name', '')
                for file in (dist.files or []):
                    pkg = file.parts[0] if file.parts else ''
                    if pkg:
                        pkg_to_dist.setdefault(pkg, []).append(dist_name)
            except Exception:
                pass
        return pkg_to_dist
    importlib.metadata.packages_distributions = packages_distributions

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
os.environ['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY')
client = genai.Client()

# Try different models
models_to_try = [
    "gemini-1.5-flash",
    "gemini-1.5-pro", 
    "gemini-2.0-flash-exp",
    "gemini-pro"
]

for model_name in models_to_try:
    print(f'\nTrying model: {model_name}...')
    try:
        response = client.models.generate_content(
            model=model_name,
            contents="Say hello"
        )
        print(f'✅ {model_name} works! Response: {response.text[:50]}')
        break
    except Exception as e:
        print(f'❌ {model_name} failed: {str(e)[:100]}')
