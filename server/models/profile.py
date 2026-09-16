from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class SkillVector(BaseModel):
    core_languages: List[str] = []
    frameworks: List[str] = []
    databases: List[str] = []
    tools_devops: List[str] = []
    concepts: List[str] = []
    all_skills: List[str] = []
    total_skills_count: int = 0
    experience_level: str = "Fresher"

class GitHubData(BaseModel):
    username: str = ""
    public_repos: int = 0
    top_languages: List[str] = []
    stars_count: int = 0
    contributions_summary: str = ""

class LeetCodeData(BaseModel):
    username: str = ""
    total_solved: int = 0
    easy_solved: int = 0
    medium_solved: int = 0
    hard_solved: int = 0
    ranking: Optional[int] = None

class CandidateProfile(BaseModel):
    id: Optional[str] = None
    user_id: str
    full_name: str = ""
    email: str = ""
    phone: str = ""
    target_roles: List[str] = ["Software Engineer", "Backend Developer"]
    target_location: str = "India (Bangalore, Hyderabad, Remote)"
    work_mode: str = "Remote / Hybrid"
    experience_years: float = 0.0
    education: str = "B.Tech / B.E. in Computer Science"
    graduation_year: int = 2026
    
    # Raw Resume Details
    resume_filename: Optional[str] = None
    resume_text_snippet: Optional[str] = None
    
    # Public Handles & Stats
    github_username: Optional[str] = None
    github_data: Optional[GitHubData] = None
    leetcode_username: Optional[str] = None
    leetcode_data: Optional[LeetCodeData] = None
    
    # Skill Vector & Readiness
    skill_vector: SkillVector = Field(default_factory=SkillVector)
    overall_readiness_score: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    target_roles: Optional[List[str]] = None
    target_location: Optional[str] = None
    work_mode: Optional[str] = None
    education: Optional[str] = None
    graduation_year: Optional[int] = None
    github_username: Optional[str] = None
    leetcode_username: Optional[str] = None
    self_reported_skills: Optional[List[str]] = None

