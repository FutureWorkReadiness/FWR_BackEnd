from setuptools import setup, find_packages

setup(
    name="gemini_generator_lib",  # The name pip will see
    version="0.1.0",
    packages=find_packages(),  # This automatically finds the 'gemini_pkg' folder
    install_requires=[
        # Dependencies are also in main requirements.txt for Docker caching
        # These are the minimum requirements for the package to work standalone
        "google-genai",
        "pydantic",
    ],
    python_requires=">=3.9",
)
