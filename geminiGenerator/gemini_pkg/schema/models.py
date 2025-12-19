from pydantic import BaseModel, model_validator
from typing import List, Optional
from gemini_pkg.config.settings import (
    word_count,
    QUESTION_WORD_MIN,
    QUESTION_WORD_MAX,
    OPTION_WORD_MIN,
    OPTION_WORD_MAX,
    RATIONALE_WORD_MAX,
    EXPLANATION_WORD_MIN,
    EXPLANATION_WORD_MAX,
)

# -------------------------------------------------
# OPTION MODEL
# -------------------------------------------------


class OptionModel(BaseModel):
    key: str
    text: str
    is_correct: bool
    rationale: str

    @model_validator(mode="after")
    def validate_option(self):
        # Validate key
        if self.key not in ("A", "B", "C", "D", "E"):
            raise ValueError("Option key must be one of: A, B, C, D, E")

        # Validate text length
        text_words = word_count(self.text)
        if not (OPTION_WORD_MIN <= text_words <= OPTION_WORD_MAX):
            raise ValueError(
                f"Option text word count {text_words} is out of range "
                f"({OPTION_WORD_MIN}-{OPTION_WORD_MAX})."
            )

        # Validate rationale
        rationale_words = word_count(self.rationale)
        if rationale_words > RATIONALE_WORD_MAX:
            raise ValueError(
                f"Rationale word count {rationale_words} exceeds max {RATIONALE_WORD_MAX}."
            )

        return self


# -------------------------------------------------
# QUESTION MODEL
# -------------------------------------------------


class QuestionModel(BaseModel):
    id: int
    question: str
    explanation: str  # Why the correct answer is correct
    options: List[OptionModel]

    @model_validator(mode="after")
    def validate_question(self):
        # Check question length
        q_words = word_count(self.question)
        if not (QUESTION_WORD_MIN <= q_words <= QUESTION_WORD_MAX):
            raise ValueError(
                f"Question word count {q_words} is out of range "
                f"({QUESTION_WORD_MIN}-{QUESTION_WORD_MAX})."
            )

        # Check explanation length
        exp_words = word_count(self.explanation)
        if not (EXPLANATION_WORD_MIN <= exp_words <= EXPLANATION_WORD_MAX):
            raise ValueError(
                f"Explanation word count {exp_words} is out of range "
                f"({EXPLANATION_WORD_MIN}-{EXPLANATION_WORD_MAX})."
            )

        # Must have exactly 5 options
        if len(self.options) != 5:
            raise ValueError("Each question must contain exactly 5 options.")

        # Must have exactly 1 correct option
        correct_count = sum(1 for opt in self.options if opt.is_correct)
        if correct_count != 1:
            raise ValueError("There must be exactly one correct option.")

        return self


# -------------------------------------------------
# QUIZ POOL MODEL
# -------------------------------------------------


class QuizPoolModel(BaseModel):
    quiz_pool: List[QuestionModel]

    @model_validator(mode="after")
    def validate_pool(self):
        if not self.quiz_pool:
            raise ValueError("quiz_pool must not be empty.")
        return self
