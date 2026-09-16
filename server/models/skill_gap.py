from typing import List, Optional
from pydantic import BaseModel, Field

class LearningResource(BaseModel):
    provider: str  # NPTEL | YouTube | Official Documentation | GitHub
    title: str
    url: str
    resource_type: str  # ACADEMIC_COURSE | PRACTICAL_VIDEO | DOCUMENTATION | HANDS_ON
    cost: str = "FREE"
    time_commitment: str
    description: str = ""

class SkillGap(BaseModel):
    skill: str
    priority: str  # CRITICAL | HIGH | MEDIUM | LOW
    frequency_count: int
    frequency_percentage: float
    market_context: str
    current_evidence: str
    suggested_action: str
    estimated_days: str
    resources: List[LearningResource] = []

class LearningPlanWeek(BaseModel):
    week_number: int
    focus_topic: str
    skills: List[str]
    tasks: List[str]
    resources: List[LearningResource]

class LearningPlan(BaseModel):
    id: Optional[str] = None
    user_id: str
    target_role: str
    total_gaps_identified: int
    weeks: List[LearningPlanWeek] = []
    generated_at: Optional[str] = None

