from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from server.database import get_applications_col, get_jobs_col, get_profiles_col, get_tailored_resumes_col
from server.routers.auth_deps import get_current_user
from server.agents.application_agent import application_agent

router = APIRouter(prefix="/api/applications", tags=["Application Agent & HITL"])

class StageRequest(BaseModel):
    job_id: str

class StatusUpdateRequest(BaseModel):
    status: str
    notes: Optional[str] = None

@router.get("")
async def get_applications(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    apps_col = get_applications_col()
    apps = await apps_col.find({"user_id": user_id})
    for a in apps:
        a["id"] = str(a.get("_id") or a.get("id"))
    return sorted(apps, key=lambda x: x.get("updated_at", ""), reverse=True)

@router.post("/stage")
async def stage_application(req: StageRequest, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    jobs_col = get_jobs_col()
    job = await jobs_col.find_one({"$or": [{"_id": req.job_id}, {"id": req.job_id}]})
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")

    profiles_col = get_profiles_col()
    profile = await profiles_col.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found")

    # Check if a tailored resume exists for this job
    resumes_col = get_tailored_resumes_col()
    tailored_resume = await resumes_col.find_one({"user_id": user_id, "job_id": req.job_id})
    tailored_filename = f"tailored_resume_{job.get('company', 'company').lower()}.pdf" if tailored_resume else profile.get("resume_filename")

    staged_app = await application_agent.stage_application(
        user_id=user_id,
        job=job,
        candidate_profile=profile,
        tailored_resume_filename=tailored_filename
    )
    return staged_app

@router.post("/{app_id}/confirm")
async def confirm_application(app_id: str, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    confirmed_app = await application_agent.confirm_submission(user_id=user_id, application_id=app_id)
    if confirmed_app.get("status") == "error":
        raise HTTPException(status_code=404, detail=confirmed_app.get("message"))
    return {
        "message": "Application manually confirmed and submitted by candidate. ToS compliant.",
        "application": confirmed_app
    }

@router.put("/{app_id}/status")
async def update_application_status(
    app_id: str,
    update: StatusUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    user_id = str(current_user["_id"])
    apps_col = get_applications_col()
    app = await apps_col.find_one({"_id": app_id, "user_id": user_id})
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    update_payload = {
        "status": update.status,
        "updated_at": datetime.utcnow().isoformat()
    }
    if update.notes is not None:
        update_payload["notes"] = update.notes

    await apps_col.update_one({"_id": app_id}, {"$set": update_payload})
    app.update(update_payload)
    app["id"] = str(app.get("_id", app_id))
    return app

@router.delete("/{app_id}")
async def delete_application(app_id: str, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    apps_col = get_applications_col()
    res = await apps_col.delete_one({"_id": app_id, "user_id": user_id})
    if res["deleted_count"] == 0:
        raise HTTPException(status_code=404, detail="Application not found")
    return {"message": "Application removed from pipeline."}

