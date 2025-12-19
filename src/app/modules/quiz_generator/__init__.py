"""
Quiz Generator module.

Provides endpoints and services for generating interview questions
using the Gemini AI API.

This module wraps the gemini_pkg package and exposes its functionality
through REST API endpoints.
"""

from src.app.modules.quiz_generator.models import GenerationJob
from src.app.modules.quiz_generator.service import QuizGeneratorService

__all__ = ["GenerationJob", "QuizGeneratorService"]

