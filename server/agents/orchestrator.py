import asyncio
from typing import Dict, Any, Optional
from server.agents.assessment_agent import assessment_agent
from server.agents.gap_learning_agent import gap_learning_agent
from server.agents.tailoring_agent import tailoring_agent
from server.agents.application_agent import application_agent
from server.agents.interview_agent import interview_agent
from server.database import db

class PipelineOrchestrator:
    """Coordinates state transitions and data handoffs across the 5 CareerPilot agents."""

    def __init__(self):
        self.name = "Pipeline Orchestrator"

    async def run_assessment_pipeline(
        self,
        resume_bytes_or_text: Any,
        github_handle: str = "",
        leetcode_handle: str = "",
        target_domain: str = "Backend"
    ) -> Dict[str, Any]:
        """Runs Agent 1 (Assessment) and Agent 2 (Gap & Learning) in sequence."""
        # 1. Agent 1: Assessment
        profile = await assessment_agent.execute(
            resume_bytes_or_text=resume_bytes_or_text,
            github_handle=github_handle,
            leetcode_handle=leetcode_handle,
            target_domain=target_domain
        )

        # 2. Agent 2: Gap & Learning
        gaps = await gap_learning_agent.execute(profile)

        return {
            "profile": profile,
            "gaps": gaps
        }

    async def run_tailoring_and_staging_pipeline(
        self,
        email: str,
        job_id: str
    ) -> Dict[str, Any]:
        """Runs Agent 3 (Tailoring) and stages through Agent 4 (Application Staging with HITL)."""
        # Retrieve Profile and Job
        profile = await db.find_one("profiles", {"email": email})
        if not profile:
            raise ValueError(f"Profile for {email} not found. Run assessment first.")

        job = await db.find_one("jobs", {"id": job_id})
        if not job:
            all_jobs = await db.find("jobs")
            job = all_jobs[0] if all_jobs else {"id": job_id, "title": "Software Engineer", "company": "Tech Corp"}

        # 1. Agent 3: Tailoring
        tailored = await tailoring_agent.execute(profile, job)

        # 2. Agent 4: Application Staging (HITL checkpoint)
        staged = await application_agent.stage_application(profile, job, tailored)

        # 3. Agent 5: Pre-generate Interview Questions for this role
        questions = await interview_agent.generate_questions(job, profile)

        return {
            "tailored": tailored,
            "staged": staged,
            "questions": questions
        }

orchestrator = PipelineOrchestrator()

