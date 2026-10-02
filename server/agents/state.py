from typing import TypedDict, List, Dict, Any, Optional

class CareerPilotState(TypedDict):
    # Candidate Baseline Data
    candidate_id: str
    raw_resume_text: str
    parsed_skills: List[str]
    candidate_name: str
    candidate_email: str
    candidate_phone: str
    github_handle: Optional[str]
    github_stats: Dict[str, Any]
    leetcode_handle: Optional[str]
    leetcode_stats: Dict[str, Any]
    target_domain: str
    overall_readiness_score: float

    # Market Intelligence & Gap Analysis
    target_jds: List[Dict[str, Any]]
    ranked_skill_gaps: List[Dict[str, Any]]
    learning_recommendations: List[Dict[str, Any]]

    # Job Tailoring Artifacts
    active_jd: Dict[str, Any]
    tailored_resume_bullets: List[Dict[str, Any]]
    tailored_cover_letter: str

    # Application Staging & HITL
    staging_portal_url: str
    staging_status: str  # "IDLE" | "STAGED_AWAITING_APPROVAL" | "USER_APPROVED_SUBMITTED"
    staged_payload: Dict[str, Any]

    # Interview Preparation Loop
    mock_questions: List[Dict[str, Any]]
    mock_evaluations: List[Dict[str, Any]]
