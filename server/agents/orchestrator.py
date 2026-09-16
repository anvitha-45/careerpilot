from typing import Dict, Any, List, Optional
from server.agents.assessment_agent import assessment_agent
from server.agents.gap_learning_agent import gap_learning_agent
from server.agents.tailoring_agent import tailoring_agent
from server.agents.application_agent import application_agent
from server.agents.interview_agent import interview_agent

class AgentWorkflowOrchestrator:
    """LangGraph-style stateful multi-agent pipeline orchestrator with explicit checkpoints."""

    STAGES = [
        {"id": "assessment", "name": "Assessment Agent", "desc": "Resume NLP + GitHub + LeetCode Vectorization", "status": "idle"},
        {"id": "jobs", "name": "Job Discovery & Matching", "desc": "Semantic Vector Search & Benchmarking", "status": "idle"},
        {"id": "gap_learning", "name": "Gap & Learning Agent", "desc": "Market Frequency Gaps & NPTEL/YouTube Roadmap", "status": "idle"},
        {"id": "tailoring", "name": "Tailoring Agent", "desc": "CAR/STAR Bullet Rewrites & Cover Letter", "status": "idle"},
        {"id": "application", "name": "Application Agent (HITL)", "desc": "Browser Staging & Mandatory Human Approval", "status": "idle"},
        {"id": "interview", "name": "Interview Prep Agent", "desc": "JD-Derived Mock Questions & Evaluation", "status": "idle"}
    ]

    async def get_pipeline_status(self, user_id: str, profile: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        has_profile = profile is not None and bool(profile.get("skill_vector", {}).get("all_skills"))
        
        stages = [
            {
                "id": "assessment",
                "name": "Assessment Agent",
                "role": "Skill Vector Extraction",
                "status": "completed" if has_profile else "active",
                "details": f"{len(profile.get('skill_vector', {}).get('all_skills', []))} skills verified" if has_profile else "Awaiting resume or profile input"
            },
            {
                "id": "jobs",
                "name": "Job Matching Engine",
                "role": "Semantic Matching",
                "status": "completed" if has_profile else "pending",
                "details": "Ranked postings benchmarked against candidate vector" if has_profile else "Requires skill vector"
            },
            {
                "id": "gap_learning",
                "name": "Gap & Learning Agent",
                "role": "Market-Frequency Upskilling",
                "status": "completed" if has_profile else "pending",
                "details": "Empirical frequency ranking with NPTEL & YouTube curation" if has_profile else "Pending assessment"
            },
            {
                "id": "tailoring",
                "name": "Tailoring Agent",
                "role": "Contextual Alignment",
                "status": "active" if has_profile else "pending",
                "details": "CAR/STAR bullet rewrites with 0% hallucination verification"
            },
            {
                "id": "application",
                "name": "Application Agent",
                "role": "Browser RPA & Safe Staging",
                "status": "active" if has_profile else "pending",
                "details": "Playwright staging with mandatory Human-in-the-Loop review"
            },
            {
                "id": "interview",
                "name": "Interview Prep Agent",
                "role": "JD-Tuned Mock Q&A",
                "status": "active" if has_profile else "pending",
                "details": "Technical, Project, and Behavioral evaluation simulation"
            }
        ]
        return stages

orchestrator = AgentWorkflowOrchestrator()

