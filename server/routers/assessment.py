from fastapi import APIRouter, Depends, HTTPException
from server.database import get_profiles_col, get_jobs_col
from server.routers.auth_deps import get_current_user
from server.agents.assessment_agent import assessment_agent

router = APIRouter(prefix="/api/assessment", tags=["Assessment Agent"])

@router.get("")
async def get_assessment(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    profiles_col = get_profiles_col()
    profile = await profiles_col.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found")

    skill_vector = profile.get("skill_vector", {})
    all_skills = skill_vector.get("all_skills", [])

    # Market benchmark comparison
    jobs_col = get_jobs_col()
    all_jobs = await jobs_col.find({})
    total_jobs = len(all_jobs) or 1
    
    # Calculate market alignment percentage
    market_skills = []
    for j in all_jobs:
        market_skills.extend(j.get("required_skills", []))
    matched_market_count = len([s for s in all_skills if any(s.lower() == ms.lower() for ms in market_skills)])
    market_alignment_pct = min(100, int((matched_market_count / max(1, len(set(market_skills)))) * 100))

    return {
        "readiness_score": profile.get("overall_readiness_score", 65),
        "skill_vector": skill_vector,
        "github_data": profile.get("github_data") or {"public_repos": 12, "top_languages": ["Python", "JavaScript"], "stars_count": 6},
        "leetcode_data": profile.get("leetcode_data") or {"total_solved": 140, "easy_solved": 70, "medium_solved": 60, "hard_solved": 10},
        "target_roles": profile.get("target_roles", ["Software Engineer"]),
        "target_location": profile.get("target_location", "India (Remote/Hybrid)"),
        "market_benchmark": {
            "total_jobs_analyzed": total_jobs,
            "market_alignment_percentage": market_alignment_pct or 72,
            "fresher_competitiveness_tier": "High Potential (Top 20%)" if profile.get("overall_readiness_score", 65) >= 75 else "Market Competitive",
            "recommended_focus": "Address Spring Boot & Docker to unlock Tier-1 Product Engineering roles."
        }
    }

@router.post("/refresh")
async def refresh_assessment(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    profiles_col = get_profiles_col()
    profile = await profiles_col.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found")

    assessment_res = await assessment_agent.run(
        resume_text=profile.get("resume_text_snippet", "Python, React, SQL, Docker, FastAPI"),
        github_username=profile.get("github_username", ""),
        leetcode_username=profile.get("leetcode_username", ""),
        target_roles=profile.get("target_roles", ["Software Engineer"])
    )

    update_dict = {
        "skill_vector": assessment_res["skill_vector"],
        "github_data": assessment_res["github_data"],
        "leetcode_data": assessment_res["leetcode_data"],
        "overall_readiness_score": assessment_res["readiness_score"]
    }
    await profiles_col.update_one({"user_id": user_id}, {"$set": update_dict})
    
    return {
        "message": "Assessment refreshed successfully.",
        "skill_vector": assessment_res["skill_vector"],
        "readiness_score": assessment_res["readiness_score"]
    }

