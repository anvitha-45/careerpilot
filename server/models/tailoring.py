from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class BulletComparison(BaseModel):
    original_bullet: str
    tailored_bullet: str
    rationale: str
    framework: str = "CAR/STAR"

class TailorRequest(BaseModel):
    job_id: str

class TailoredResume(BaseModel):
    id: Optional[str] = None
    user_id: str
    job_id: str
    company_name: str
    role_title: str
    summary_statement: str
    reordered_skills: List[str]
    bullet_rewrites: List[BulletComparison]
    highlighted_projects: List[str]
    zero_hallucination_verified: bool = True
    verified_terms_count: int = 0
    pdf_download_url: Optional[str] = None
    created_at: Optional[str] = None

class CoverLetter(BaseModel):
    id: Optional[str] = None
    user_id: str
    job_id: str
    company_name: str
    role_title: str
    hook: str
    value_proposition: str
    problem_solving_proof: str
    cultural_alignment: str
    call_to_action: str
    full_text: str
    created_at: Optional[str] = None

