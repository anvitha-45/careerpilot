from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class InterviewQuestion(BaseModel):
    id: str
    category: str  # TECHNICAL | PROJECT_DEEP_DIVE | BEHAVIORAL | CS_FOUNDATIONS
    question: str
    context: str
    expected_key_points: List[str] = []
    sample_ideal_answer: str = ""

class AnswerSubmission(BaseModel):
    question_id: str
    candidate_answer: str

class QuestionFeedback(BaseModel):
    question_id: str
    question_text: str
    candidate_answer: str
    score: int = Field(ge=0, le=10)  # out of 10
    technical_accuracy: str
    depth_of_explanation: str
    communication_clarity: str
    improvement_suggestions: List[str] = []

class InterviewEvaluation(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    readiness_level: str  # READY | PROMISING | NEEDS_PREPARATION
    strengths: List[str] = []
    critical_gaps: List[str] = []
    question_feedbacks: List[QuestionFeedback] = []
    summary: str = ""

class InterviewSession(BaseModel):
    id: Optional[str] = None
    user_id: str
    job_id: str
    company_name: str
    role_title: str
    status: str = "READY"  # READY | IN_PROGRESS | COMPLETED
    questions: List[InterviewQuestion] = []
    answers: Dict[str, str] = {}  # question_id -> candidate_answer
    evaluation: Optional[InterviewEvaluation] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None

