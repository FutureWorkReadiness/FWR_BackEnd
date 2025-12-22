"""
Quiz, Question, and Attempt schemas.
Pydantic models for the quiz system.

New format (v2):
- Questions have question_text, question_type, points, explanation
- Options have key (A-E), text, is_correct, rationale
- 5 options per question (A, B, C, D, E)
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID


# ============================================================
# OPTION SCHEMAS
# ============================================================


class OptionBase(BaseModel):
    """Base schema for question options."""

    key: str = Field(..., description="Option key: A, B, C, D, or E")
    text: str = Field(..., description="The option text (10-24 words)")
    is_correct: bool = Field(
        default=False, description="Whether this is the correct answer"
    )
    rationale: Optional[str] = Field(
        None, description="Why this option is correct/incorrect"
    )


class OptionCreate(OptionBase):
    """Schema for creating a new option."""

    pass


class OptionResponse(OptionBase):
    """Schema for option in API responses."""

    option_id: UUID

    class Config:
        from_attributes = True


class OptionInQuiz(BaseModel):
    """Option as shown during quiz (without revealing correct answer)."""

    key: str
    text: str

    class Config:
        from_attributes = True


class OptionWithAnswer(OptionInQuiz):
    """Option with answer revealed (after submission)."""

    is_correct: bool
    rationale: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================================
# QUESTION SCHEMAS
# ============================================================


class QuestionBase(BaseModel):
    """Base schema for questions."""

    question_text: str = Field(..., description="The question text (12-28 words)")
    question_type: str = Field(default="multiple_choice", description="Question type")
    points: int = Field(default=1, description="Points for this question")
    explanation: Optional[str] = Field(
        None, description="Explanation shown after answer (15-50 words)"
    )


class QuestionCreate(QuestionBase):
    """Schema for creating a question."""

    options: List[OptionCreate] = Field(..., min_length=5, max_length=5)


class QuestionResponse(QuestionBase):
    """Schema for question in API responses."""

    question_id: UUID
    quiz_id: UUID
    order_index: int
    options: List[OptionResponse] = []

    class Config:
        from_attributes = True


class QuestionInQuiz(BaseModel):
    """Question as shown during quiz (options without answers revealed)."""

    question_id: str
    question_text: str
    question_type: str
    points: int
    order_index: int
    options: List[OptionInQuiz]

    class Config:
        from_attributes = True


class QuestionWithAnswer(BaseModel):
    """Question with answers revealed (after submission)."""

    question_id: str
    question_text: str
    question_type: str
    points: int
    explanation: Optional[str] = None
    options: List[OptionWithAnswer]
    correct_key: str  # The correct answer key (A, B, C, D, or E)

    class Config:
        from_attributes = True


class QuestionResult(BaseModel):
    """Result for a single question after quiz submission."""

    question_id: str
    question_text: str
    user_answer: str  # The key user selected (A, B, C, D, E)
    correct_answer: str  # The correct key
    is_correct: bool
    points: int
    earned_points: int
    explanation: Optional[str] = None
    options: List[OptionWithAnswer]


# ============================================================
# QUIZ SCHEMAS
# ============================================================


class QuizBase(BaseModel):
    """Base schema for Quiz data."""

    title: str
    description: Optional[str] = None
    difficulty_level: int = Field(..., ge=1, le=5, description="Difficulty 1-5")
    time_limit_minutes: int = Field(default=30)
    passing_score: float = Field(default=70.0)


class QuizCreate(QuizBase):
    """Schema for creating a quiz."""

    specialization_id: UUID
    questions: List[QuestionCreate]


class QuizSummary(BaseModel):
    """Schema for Quiz listing (without questions)."""

    quiz_id: str
    title: str
    description: Optional[str] = None
    difficulty_level: int
    time_limit_minutes: int
    passing_score: float
    question_count: int
    specialization_id: str
    specialization_name: Optional[str] = None

    class Config:
        from_attributes = True


class QuizDetail(BaseModel):
    """Schema for quiz detail (with questions, for taking quiz)."""

    quiz_id: str
    title: str
    description: Optional[str] = None
    difficulty_level: int
    time_limit_minutes: int
    passing_score: float
    question_count: int
    specialization_id: str
    questions: List[QuestionInQuiz]

    class Config:
        from_attributes = True


class QuizWithAnswers(BaseModel):
    """Schema for quiz with answers revealed (after submission)."""

    quiz_id: str
    title: str
    description: Optional[str] = None
    difficulty_level: int
    questions: List[QuestionWithAnswer]

    class Config:
        from_attributes = True


# ============================================================
# QUIZ SUBMISSION SCHEMAS
# ============================================================


class QuizAnswer(BaseModel):
    """Schema for a single quiz answer."""

    question_id: UUID
    selected_key: str = Field(
        ..., pattern="^[A-E]$", description="Selected option key (A-E)"
    )


class QuizSubmission(BaseModel):
    """Schema for submitting quiz answers."""

    answers: List[QuizAnswer]


# ============================================================
# QUIZ ATTEMPT SCHEMAS
# ============================================================


class QuizAttemptBase(BaseModel):
    """Base schema for quiz attempt."""

    user_id: UUID
    quiz_id: UUID


class QuizAttemptResponse(BaseModel):
    """Schema for quiz attempt response."""

    attempt_id: str
    quiz_id: str
    user_id: str
    score: Optional[float] = None
    max_score: Optional[float] = None
    percentage: Optional[float] = None
    time_taken_minutes: Optional[int] = None
    is_passed: Optional[bool] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class QuizStartResponse(BaseModel):
    """Response schema for starting a quiz."""

    attempt_id: str
    quiz_id: str
    quiz: QuizDetail
    message: str


# ============================================================
# QUIZ RESULT SCHEMAS
# ============================================================


class ReadinessSnapshot(BaseModel):
    """Snapshot of user's readiness scores."""

    overall: float
    technical: float
    soft: float


class FeedbackDetail(BaseModel):
    """Detailed feedback for quiz performance."""

    overall: str
    strengths: str
    weaknesses: str
    recommendations: List[str]


class ScoreImpact(BaseModel):
    """Impact of quiz on user scores."""

    category: str
    old_score: float
    new_score: float
    increase: float


class QuizResult(BaseModel):
    """Schema for quiz result after submission."""

    success: bool
    score: float
    max_score: float
    percentage: float
    correct_count: int
    total_count: int
    passed: bool
    message: str
    quiz_title: str
    passing_score: float
    time_taken_minutes: Optional[int] = None


class QuizResultExtended(QuizResult):
    """Extended quiz result with detailed feedback."""

    readiness: ReadinessSnapshot
    feedback: Optional[FeedbackDetail] = None
    question_results: List[QuestionResult] = []
    score_impact: Optional[ScoreImpact] = None


class UpdatedGoalItem(BaseModel):
    """Auto-updated goal after quiz submission."""

    goal_id: str
    title: str
    old_value: float
    new_value: float
    is_completed: bool


class QuizSubmitResponse(QuizResultExtended):
    """Response schema for POST /quizzes/attempts/{attempt_id}/submit."""

    updated_goals: List[UpdatedGoalItem] = []


# ============================================================
# LIST RESPONSE SCHEMAS
# ============================================================


class QuizListResponse(BaseModel):
    """Response schema for GET /quizzes/."""

    quizzes: List[QuizSummary]
    total: int


class AttemptInfo(BaseModel):
    """Attempt information in result response."""

    attempt_id: str
    quiz_id: str
    score: Optional[float] = None
    percentage: Optional[float] = None
    passed: Optional[bool] = None
    completed_at: Optional[str] = None


class QuizInfo(BaseModel):
    """Quiz information in result response."""

    quiz_id: str
    title: str
    description: Optional[str] = None
    difficulty_level: int
    passing_score: float


class AttemptResultResponse(BaseModel):
    """Response schema for GET /quizzes/attempts/{attempt_id}/results."""

    attempt: AttemptInfo
    quiz: QuizInfo
    question_results: List[QuestionResult]
    readiness: ReadinessSnapshot
