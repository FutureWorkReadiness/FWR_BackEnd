"""
Test using the older genai.configure() approach instead of Client()
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
api_key = os.getenv('GEMINI_API_KEY')

print(f'Using API key: {api_key[:10]}...{api_key[-4:]}')
print('\nConfiguring genai...')

# Use the older configure approach
genai.configure(api_key=api_key)

print('Testing simple generation...')
try:
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Say hello in one short sentence")
    print(f'✅ SUCCESS! Response: {response.text}')
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
