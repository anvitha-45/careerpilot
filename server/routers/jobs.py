from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from server.database import get_jobs_col, get_profiles_col, get_applications_col
from server.routers.auth_deps import get_current_user
from server.services.vector_service import vector_service

router = APIRouter(prefix="/api/jobs", tags=["Jobs & Matching"])

class JobImportRequest(BaseModel):
    title: str
    company: str
    location: str = "Bengaluru, India"
    work_mode: str = "Hybrid"
    portal: str = "LinkedIn"
    apply_url: str = ""
    description: str
    required_skills: List[str] = []
    preferred_skills: List[str] = []

@router.get("")
async def get_jobs(
    search: Optional[str] = None,
    portal: Optional[str] = None,
    min_score: int = Query(default=0, ge=0, le=100),
    current_user: dict = Depends(get_current_user)
):
    user_id = str(current_user["_id"])
    profiles_col = get_profiles_col()
    profile = await profiles_col.find_one({"user_id": user_id})
    candidate_skills = profile.get("skill_vector", {}).get("all_skills", []) if profile else []
    candidate_roles = profile.get("target_roles", ["Software Engineer"]) if profile else ["Software Engineer"]
    candidate_loc = profile.get("target_location", "India") if profile else "India"

    jobs_col = get_jobs_col()
    query = {}
    if portal and portal.lower() != "all":
        query["portal"] = {"$regex": portal, "$options": "i"}
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"company": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]

    all_jobs = await jobs_col.find(query)
    
    # Check applications to mark shortlisted / applied status
    apps_col = get_applications_col()
    user_apps = await apps_col.find({"user_id": user_id})
    app_status_map = {str(app.get("job_id")): app.get("status") for app in user_apps}

    scored_jobs = []
    for job in all_jobs:
        job_id = str(job.get("_id") or job.get("id"))
        match_result = vector_service.compute_match(
            candidate_skills=candidate_skills,
            required_skills=job.get("required_skills", []),
            preferred_skills=job.get("preferred_skills", []),
            candidate_target_roles=candidate_roles,
            job_title=job.get("title", ""),
            candidate_location=candidate_loc,
            job_location=job.get("location", "")
        )

        if match_result["match_score"] >= min_score:
            job_copy = dict(job)
            job_copy["id"] = job_id
            scored_jobs.append({
                "job": job_copy,
                "match_score": match_result["match_score"],
                "matched_skills": match_result["matched_skills"],
                "missing_skills": match_result["missing_skills"],
                "explanation": match_result["explanation"],
                "status": app_status_map.get(job_id, "DISCOVERED")
            })

    # Sort descending by match score
    scored_jobs.sort(key=lambda x: x["match_score"], reverse=True)
    return scored_jobs

@router.get("/{job_id}")
async def get_job_detail(job_id: str, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    jobs_col = get_jobs_col()
    job = await jobs_col.find_one({"$or": [{"_id": job_id}, {"id": job_id}]})
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")

    profiles_col = get_profiles_col()
    profile = await profiles_col.find_one({"user_id": user_id})
    candidate_skills = profile.get("skill_vector", {}).get("all_skills", []) if profile else []
    candidate_roles = profile.get("target_roles", ["Software Engineer"]) if profile else ["Software Engineer"]
    candidate_loc = profile.get("target_location", "India") if profile else "India"

    match_result = vector_service.compute_match(
        candidate_skills=candidate_skills,
        required_skills=job.get("required_skills", []),
        preferred_skills=job.get("preferred_skills", []),
        candidate_target_roles=candidate_roles,
        job_title=job.get("title", ""),
        candidate_location=candidate_loc,
        job_location=job.get("location", "")
    )

    apps_col = get_applications_col()
    app = await apps_col.find_one({"user_id": user_id, "job_id": job_id})

    job_copy = dict(job)
    job_copy["id"] = str(job.get("_id") or job.get("id"))

    return {
        "job": job_copy,
        "match_score": match_result["match_score"],
        "skills_score": match_result["skills_score"],
        "role_relevance_score": match_result["role_relevance_score"],
        "project_evidence_score": match_result["project_evidence_score"],
        "location_score": match_result["location_score"],
        "matched_skills": match_result["matched_skills"],
        "missing_skills": match_result["missing_skills"],
        "explanation": match_result["explanation"],
        "application_status": app.get("status") if app else "DISCOVERED"
    }

@router.post("/import")
async def import_job(import_data: JobImportRequest, current_user: dict = Depends(get_current_user)):
    jobs_col = get_jobs_col()
    
    # Deduce skills if not explicitly provided
    req_skills = import_data.required_skills
    if not req_skills:
        from server.services.resume_parser import resume_parser
        parsed = resume_parser.parse(import_data.description)
        req_skills = parsed["all_skills"][:5] or ["Python", "SQL", "Git"]

    doc = {
        "title": import_data.title,
        "company": import_data.company,
        "location": import_data.location,
        "region": "India",
        "work_mode": import_data.work_mode,
        "experience_required": "0-2 years",
        "salary_range": "₹8 - 14 LPA",
        "portal": import_data.portal,
        "apply_url": import_data.apply_url or "https://linkedin.com/jobs",
        "description": import_data.description,
        "required_skills": req_skills,
        "preferred_skills": import_data.preferred_skills or ["Docker", "AWS"],
        "source": "User Imported",
        "created_at": datetime.utcnow().isoformat()
    }
    res = await jobs_col.insert_one(doc)
    doc["id"] = str(res["inserted_id"])
    return {"message": "Job description imported successfully.", "job": doc}

