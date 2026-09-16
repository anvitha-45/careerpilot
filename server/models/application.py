from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class StagingField(BaseModel):
    field_name: str
    field_type: str  # text | email | tel | file | select
    staged_value: str
    is_verified: bool = True

class StagingSession(BaseModel):
    session_id: str
    job_id: str
    portal: str
    apply_url: str
    staged_fields: List[StagingField] = []
    status: str = "READY_FOR_REVIEW"  # PREPARING | READY_FOR_REVIEW | USER_SUBMITTED | FAILED
    browser_active: bool = False
    review_checklist: List[str] = [
        "Personal Contact Information Verified",
        "Tailored Resume PDF Attached",
        "Cover Letter Verified",
        "Work Authorization Disclosures Confirmed",
        "Terms of Service Respected (Manual Final Submit)"
    ]
    staged_at: Optional[str] = None

class JobApplication(BaseModel):
    id: Optional[str] = None
    user_id: str
    job_id: str
    job_title: str
    company_name: str
    portal: str
    apply_url: str
    status: str = "SHORTLISTED"  # SHORTLISTED | PREPARING | READY_FOR_REVIEW | USER_SUBMITTED | INTERVIEW | OFFER | REJECTED
    tailored_resume_id: Optional[str] = None
    cover_letter_id: Optional[str] = None
    staging_session: Optional[StagingSession] = None
    notes: str = ""
    applied_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

