from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class JobItem(BaseModel):
    id: Optional[str] = None
    title: str
    company: str
    location: str
    region: str = "India"
    work_mode: str = "Hybrid"  # Remote | Hybrid | On-site
    experience_required: str = "0-1 years"
    salary_range: str = "₹6-12 LPA"
    portal: str = "LinkedIn"  # LinkedIn | Naukri | Direct ATS
    apply_url: str = ""
    description: str = ""
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    source: str = "Aggregated"
    created_at: Optional[str] = None

class JobMatch(BaseModel):
    id: Optional[str] = None
    job_id: str
    user_id: str
    job: Optional[JobItem] = None
    match_score: int = Field(ge=0, le=100)
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    role_relevance_score: int = 0
    skills_score: int = 0
    project_evidence_score: int = 0
    explanation: str = ""
    status: str = "DISCOVERED"  # DISCOVERED | SHORTLISTED | APPLIED | REJECTED

class JobQuery(BaseModel):
    role: Optional[str] = None
    location: Optional[str] = None
    portal: Optional[str] = None
    min_score: Optional[int] = 0
    search: Optional[str] = None

