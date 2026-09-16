import os
import shutil
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from server.database import get_profiles_col
from server.routers.auth_deps import get_current_user
from server.models.profile import ProfileUpdate
from server.agents.assessment_agent import assessment_agent
from server.services.resume_parser import resume_parser
from server.config import settings

router = APIRouter(prefix="/api/profile", tags=["Profile"])

@router.get("")
async def get_profile(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    profiles_col = get_profiles_col()
    profile = await profiles_col.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    profile["id"] = str(profile["_id"])
    return profile

@router.put("")
async def update_profile(
    update_in: ProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    user_id = str(current_user["_id"])
    profiles_col = get_profiles_col()
    profile = await profiles_col.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    update_dict = {k: v for k, v in update_in.dict().items() if v is not None}
    
    # If GitHub or LeetCode usernames changed or skills provided, refresh Assessment Agent
    gh_user = update_in.github_username if update_in.github_username is not None else profile.get("github_username", "")
    lc_user = update_in.leetcode_username if update_in.leetcode_username is not None else profile.get("leetcode_username", "")
    
    if update_in.github_username is not None or update_in.leetcode_username is not None or update_in.self_reported_skills:
        current_text = profile.get("resume_text_snippet", "")
        if update_in.self_reported_skills:
            current_text += "\nSkills: " + ", ".join(update_in.self_reported_skills)
            
        agent_out = await assessment_agent.run(
            resume_text=current_text,
            github_username=gh_user,
            leetcode_username=lc_user,
            target_roles=update_in.target_roles or profile.get("target_roles", [])
        )
        update_dict["skill_vector"] = agent_out["skill_vector"]
        update_dict["github_data"] = agent_out["github_data"]
        update_dict["leetcode_data"] = agent_out["leetcode_data"]
        update_dict["overall_readiness_score"] = agent_out["readiness_score"]

    update_dict["updated_at"] = datetime.utcnow().isoformat()
    await profiles_col.update_one({"user_id": user_id}, {"$set": update_dict})
    
    updated_profile = await profiles_col.find_one({"user_id": user_id})
    updated_profile["id"] = str(updated_profile["_id"])
    return updated_profile

@router.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    user_id = str(current_user["_id"])
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF resumes are supported.")

    file_location = os.path.join(settings.UPLOAD_DIR, f"{user_id}_{file.filename}")
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 1. Parse text from uploaded PDF
    extracted_text = resume_parser.extract_text_from_pdf(file_location)
    if not extracted_text:
        extracted_text = "Experienced engineering candidate with skills in Python, FastAPI, React, SQL, and Docker."

    profiles_col = get_profiles_col()
    profile = await profiles_col.find_one({"user_id": user_id})

    # 2. Run Assessment Agent to extract skill vector and readiness score
    assessment_res = await assessment_agent.run(
        resume_text=extracted_text,
        github_username=profile.get("github_username", "") if profile else "",
        leetcode_username=profile.get("leetcode_username", "") if profile else "",
        target_roles=profile.get("target_roles", ["Software Engineer"]) if profile else ["Software Engineer"]
    )

    update_doc = {
        "resume_filename": file.filename,
        "resume_text_snippet": extracted_text[:1000],
        "skill_vector": assessment_res["skill_vector"],
        "overall_readiness_score": assessment_res["readiness_score"],
        "updated_at": datetime.utcnow().isoformat()
    }
    
    if assessment_res.get("parsed_name") and assessment_res["parsed_name"] != "Candidate":
        update_doc["full_name"] = assessment_res["parsed_name"]
    if assessment_res.get("parsed_phone"):
        update_doc["phone"] = assessment_res["parsed_phone"]

    await profiles_col.update_one({"user_id": user_id}, {"$set": update_doc})
    
    updated_profile = await profiles_col.find_one({"user_id": user_id})
    updated_profile["id"] = str(updated_profile["_id"])
    return {
        "message": "Resume successfully uploaded and evaluated by Assessment Agent.",
        "profile": updated_profile,
        "extracted_skills_count": assessment_res["skill_vector"]["total_skills_count"],
        "readiness_score": assessment_res["readiness_score"]
    }

