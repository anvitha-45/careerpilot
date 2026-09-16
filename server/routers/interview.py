from datetime import datetime
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from server.database import get_interviews_col, get_jobs_col
from server.routers.auth_deps import get_current_user
from server.agents.interview_agent import interview_agent

router = APIRouter(prefix="/api/interview", tags=["Interview Prep Agent"])

class StartInterviewRequest(BaseModel):
    job_id: str

class SubmitAnswersRequest(BaseModel):
    answers: Dict[str, str]  # question_id -> candidate_answer

@router.post("/start")
async def start_interview(req: StartInterviewRequest, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    jobs_col = get_jobs_col()
    job = await jobs_col.find_one({"$or": [{"_id": req.job_id}, {"id": req.job_id}]})
    if not job:
        raise HTTPException(status_code=404, detail="Target job not found")

    questions = await interview_agent.generate_questions_for_job(job)
    
    session_doc = {
        "user_id": user_id,
        "job_id": req.job_id,
        "company_name": job.get("company", "Company"),
        "role_title": job.get("title", "Software Engineer"),
        "status": "IN_PROGRESS",
        "questions": questions,
        "answers": {},
        "evaluation": None,
        "created_at": datetime.utcnow().isoformat()
    }

    interviews_col = get_interviews_col()
    res = await interviews_col.insert_one(session_doc)
    session_doc["id"] = str(res["inserted_id"])
    return session_doc

@router.post("/{session_id}/submit")
async def submit_interview(
    session_id: str,
    req: SubmitAnswersRequest,
    current_user: dict = Depends(get_current_user)
):
    user_id = str(current_user["_id"])
    interviews_col = get_interviews_col()
    session = await interviews_col.find_one({"_id": session_id, "user_id": user_id})
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    questions = session.get("questions", [])
    eval_result = await interview_agent.evaluate_answers(questions, req.answers)

    update_payload = {
        "status": "COMPLETED",
        "answers": req.answers,
        "evaluation": eval_result,
        "completed_at": datetime.utcnow().isoformat()
    }
    await interviews_col.update_one({"_id": session_id}, {"$set": update_payload})
    session.update(update_payload)
    session["id"] = str(session.get("_id", session_id))
    return session

@router.get("/sessions")
async def get_interview_sessions(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    interviews_col = get_interviews_col()
    sessions = await interviews_col.find({"user_id": user_id})
    for s in sessions:
        s["id"] = str(s.get("_id") or s.get("id"))
    return sorted(sessions, key=lambda x: x.get("created_at", ""), reverse=True)

@router.get("/{session_id}")
async def get_interview_session(session_id: str, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    interviews_col = get_interviews_col()
    session = await interviews_col.find_one({"_id": session_id, "user_id": user_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session["id"] = str(session.get("_id", session_id))
    return session

