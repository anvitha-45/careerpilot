from fastapi import APIRouter, Depends, HTTPException
from server.database import get_profiles_col
from server.routers.auth_deps import get_current_user
from server.agents.gap_learning_agent import gap_learning_agent

router = APIRouter(prefix="/api/learning", tags=["Gap & Learning Agent"])

@router.get("/gaps")
async def get_skill_gaps(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    profiles_col = get_profiles_col()
    profile = await profiles_col.find_one({"user_id": user_id})
    candidate_skills = profile.get("skill_vector", {}).get("all_skills", []) if profile else []
    target_roles = profile.get("target_roles", ["Software Engineer"]) if profile else ["Software Engineer"]

    result = await gap_learning_agent.run(
        user_id=user_id,
        candidate_skills=candidate_skills,
        target_roles=target_roles
    )
    return result

@router.get("/plan")
async def get_learning_plan(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    profiles_col = get_profiles_col()
    profile = await profiles_col.find_one({"user_id": user_id})
    candidate_skills = profile.get("skill_vector", {}).get("all_skills", []) if profile else []
    target_roles = profile.get("target_roles", ["Software Engineer"]) if profile else ["Software Engineer"]

    result = await gap_learning_agent.run(
        user_id=user_id,
        candidate_skills=candidate_skills,
        target_roles=target_roles
    )
    
    return {
        "user_id": user_id,
        "target_roles": target_roles,
        "total_gaps_identified": result["total_gaps_identified"],
        "critical_gaps_count": result["critical_gaps_count"],
        "weeks": result["weeks"]
    }

