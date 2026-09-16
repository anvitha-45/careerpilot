import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from server.services.playwright_service import playwright_service
from server.database import get_applications_col

class ApplicationAgent:
    """The innovative core: browser staging on portals (Naukri, LinkedIn, ATS) with strict Human-in-the-Loop review gate."""

    async def stage_application(
        self,
        user_id: str,
        job: Dict[str, Any],
        candidate_profile: Dict[str, Any],
        tailored_resume_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        session_id = f"stage_{uuid.uuid4().hex[:8]}"
        portal = job.get("portal", "LinkedIn")
        apply_url = job.get("apply_url", "https://linkedin.com/jobs")

        candidate_data = {
            "name": candidate_profile.get("full_name", "Engineering Candidate"),
            "email": candidate_profile.get("email", "candidate@example.com"),
            "phone": candidate_profile.get("phone", "+91 9876543210"),
            "github_username": candidate_profile.get("github_username", "developer"),
            "target_roles": candidate_profile.get("target_roles", ["Software Engineer"])
        }

        # Trigger Playwright staging session
        staging_result = await playwright_service.stage_application(
            session_id=session_id,
            portal=portal,
            apply_url=apply_url,
            candidate_data=candidate_data,
            resume_filename=tailored_resume_filename
        )

        app_doc = {
            "user_id": user_id,
            "job_id": job.get("id") or job.get("_id"),
            "job_title": job.get("title", "Software Engineer"),
            "company_name": job.get("company", "Company"),
            "portal": portal,
            "apply_url": apply_url,
            "status": "READY_FOR_REVIEW",  # HALTS at Human Review Checkpoint!
            "staging_session": {
                "session_id": session_id,
                "portal": portal,
                "apply_url": apply_url,
                "staged_fields": staging_result["staged_fields"],
                "status": "READY_FOR_REVIEW",
                "browser_active": staging_result.get("browser_active", False),
                "review_checklist": [
                    "Candidate Contact Information Verified",
                    "Tailored Resume PDF Attached",
                    "Cover Letter Verified Against Factual Data",
                    "Terms of Service Respected (No Automated Final Submit)",
                    "Applicant In Full Control"
                ],
                "staged_at": datetime.utcnow().isoformat()
            },
            "notes": "Application pre-filled via Playwright. Awaiting human confirmation.",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        apps_col = get_applications_col()
        existing = await apps_col.find_one({"user_id": user_id, "job_id": app_doc["job_id"]})
        if existing:
            await apps_col.update_one({"_id": existing["_id"]}, {"$set": app_doc})
            app_id = existing["_id"]
        else:
            res = await apps_col.insert_one(app_doc)
            app_id = res["inserted_id"]

        app_doc["id"] = str(app_id)
        return app_doc

    async def confirm_submission(self, user_id: str, application_id: str) -> Dict[str, Any]:
        """User manually confirms they have completed review and triggered submission in the browser."""
        apps_col = get_applications_col()
        app = await apps_col.find_one({"_id": application_id, "user_id": user_id})
        if not app:
            return {"status": "error", "message": "Application not found"}

        update_payload = {
            "status": "USER_SUBMITTED",
            "applied_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "notes": "User reviewed staged fields and manually confirmed submission."
        }
        await apps_col.update_one({"_id": application_id}, {"$set": update_payload})
        app.update(update_payload)
        app["id"] = str(app.get("_id", application_id))
        return app

application_agent = ApplicationAgent()

