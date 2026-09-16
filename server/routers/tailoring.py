from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from server.database import get_profiles_col, get_jobs_col, get_tailored_resumes_col
from server.routers.auth_deps import get_current_user
from server.agents.tailoring_agent import tailoring_agent

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
    doc["id"] = str(res["inserted_id"])

    return doc

@router.get("/history")
async def get_tailor_history(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    resumes_col = get_tailored_resumes_col()
    resumes = await resumes_col.find({"user_id": user_id})
    for r in resumes:
        r["id"] = str(r.get("_id") or r.get("id"))
    return sorted(resumes, key=lambda x: x.get("created_at", ""), reverse=True)

