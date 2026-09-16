from datetime import datetime
import re
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from server.database import get_profiles_col, get_jobs_col, get_tailored_resumes_col
from server.routers.auth_deps import get_current_user
from server.agents.tailoring_agent import tailoring_agent
from server.services.pdf_resume_service import pdf_resume_service

router = APIRouter(prefix="/api/tailor", tags=["Tailoring Agent"])

class TailorRequest(BaseModel):
    job_id: str

@router.post("/resume")
async def tailor_resume(req: TailorRequest, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    profiles_col = get_profiles_col()
    profile = await profiles_col.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    jobs_col = get_jobs_col()
    job = await jobs_col.find_one({"$or": [{"_id": req.job_id}, {"id": req.job_id}]})
    if not job:
        raise HTTPException(status_code=404, detail="Target job not found")

    tailored_data = await tailoring_agent.run(
        candidate_profile=profile,
        job=job
    )

    doc = {
        "user_id": user_id,
        "job_id": req.job_id,
        "company_name": tailored_data["company_name"],
        "role_title": tailored_data["role_title"],
        "summary_statement": tailored_data["summary_statement"],
        "reordered_skills": tailored_data["reordered_skills"],
        "bullet_rewrites": tailored_data["bullet_rewrites"],
        "highlighted_projects": tailored_data["highlighted_projects"],
        "zero_hallucination_verified": tailored_data["zero_hallucination_verified"],
        "verified_terms_count": tailored_data["verified_terms_count"],
        "cover_letter": tailored_data["cover_letter"],
        "created_at": datetime.utcnow().isoformat()
    }

    resumes_col = get_tailored_resumes_col()
    res = await resumes_col.insert_one(doc)
    doc["id"] = str(res.get("inserted_id") or doc.get("_id") or "tailored_1")

    return doc

@router.get("/history")
async def get_tailor_history(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    resumes_col = get_tailored_resumes_col()
    resumes = await resumes_col.find({"user_id": user_id})
    for r in resumes:
        r["id"] = str(r.get("_id") or r.get("id"))
    return sorted(resumes, key=lambda x: x.get("created_at", ""), reverse=True)

@router.get("/export-pdf")
async def export_tailored_resume_pdf(
    job_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Generates and downloads a clean, single-column ATS-compliant PDF resume."""
    user_id = str(current_user["_id"])
    profiles_col = get_profiles_col()
    profile = await profiles_col.find_one({"user_id": user_id})
    if not profile:
        profile = {
            "full_name": current_user.get("name", "Aarav Sharma"),
            "email": current_user.get("email", "candidate@careerpilot.ai"),
            "preferred_location": "Bangalore, India",
            "github_username": "developer",
            "skill_vector": {
                "languages": ["Python", "JavaScript", "SQL", "C++"],
                "frameworks": ["FastAPI", "React", "Node.js"],
                "databases": ["PostgreSQL", "MongoDB", "Redis"],
                "tools": ["Git", "Docker", "Linux"],
                "cs_foundations": ["DSA", "DBMS", "Operating Systems"]
            }
        }

    resumes_col = get_tailored_resumes_col()
    tailored_doc = None

    if job_id:
        tailored_doc = await resumes_col.find_one({"user_id": user_id, "job_id": job_id})
    
    if not tailored_doc:
        # Fallback to latest tailored resume for this user
        all_user_resumes = await resumes_col.find({"user_id": user_id})
        if all_user_resumes:
            tailored_doc = sorted(all_user_resumes, key=lambda x: x.get("created_at", ""), reverse=True)[0]

    if not tailored_doc:
        # Generate dynamically on the fly if needed
        jobs_col = get_jobs_col()
        target_job_id = job_id or "job_1"
        job = await jobs_col.find_one({"$or": [{"_id": target_job_id}, {"id": target_job_id}]})
        if not job:
            # Pick first available job
            all_jobs = await jobs_col.find({})
            job = all_jobs[0] if all_jobs else {
                "company": "Target Organization",
                "title": "Software Development Engineer",
                "required_skills": ["Python", "React", "SQL"]
            }
        tailored_doc = await tailoring_agent.run(candidate_profile=profile, job=job)

    company_name = tailored_doc.get("company_name", "TargetCompany")
    safe_company = re.sub(r'[^a-zA-Z0-9_-]', '_', company_name)
    filename = f"CareerPilot_Resume_{safe_company}.pdf"

    pdf_bytes = pdf_resume_service.generate_ats_resume_pdf(profile, tailored_doc)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )
