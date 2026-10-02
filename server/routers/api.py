import json
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from server.database import db
from server.agents.orchestrator import orchestrator
from server.agents.application_agent import application_agent
from server.agents.interview_agent import interview_agent

router = APIRouter(prefix="/api", tags=["Pipeline API"])

class TailorRequest(BaseModel):
    email: str
    job_id: str

class ConfirmApplicationRequest(BaseModel):
    application_id: str
    email: str

class InterviewEvalRequest(BaseModel):
    question: str
    user_answer: str
    role: str
    skills: List[str] = []

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "CareerPilot",
        "version": "2.0.0",
        "database": "MongoDB" if db.is_connected else "Embedded Local Document Store"
    }

@router.get("/jobs")
async def get_jobs():
    """Retrieve all available job descriptions for benchmarking."""
    jobs = await db.find("jobs")
    return {"jobs": jobs}

@router.post("/assess")
async def run_assessment(
    resume_file: Optional[UploadFile] = File(None),
    resume_text: Optional[str] = Form(None),
    full_name: Optional[str] = Form(""),
    email: Optional[str] = Form(""),
    phone: Optional[str] = Form(""),
    github_handle: Optional[str] = Form(""),
    leetcode_handle: Optional[str] = Form(""),
    target_domain: Optional[str] = Form("All")
):
    """Agent 1 + Agent 2: Ingests resume, scrapes GitHub/LeetCode, and computes market readiness and gaps."""
    content = ""
    if resume_file:
        file_bytes = await resume_file.read()
        if resume_file.filename.lower().endswith(".pdf"):
            content = file_bytes
        else:
            content = file_bytes.decode("utf-8", errors="ignore")
    elif resume_text and resume_text.strip():
        content = resume_text.strip()
    else:
        # Provide default engineering student resume text for instant 1-click test
        display_name = full_name.strip() or "Ananya Sharma"
        display_email = email.strip() or "ananya.sharma@example.com"
        display_phone = phone.strip() or "+91 9876543210"
        content = f"""
        {display_name.upper()}
        Email: {display_email} | Phone: {display_phone}
        GitHub: github.com/{github_handle or 'developer'} | LinkedIn: linkedin.com/in/{display_name.lower().replace(' ', '-')}
        
        EDUCATION
        B.Tech in Computer Science and Engineering (2022 - 2026)
        CGPA: 8.7/10
        
        TECHNICAL SKILLS
        Languages: Python, JavaScript, TypeScript, SQL, HTML5, CSS3
        Frameworks: FastAPI, React, Flask, Scikit-Learn, Pandas
        Databases: PostgreSQL, Redis, SQLite
        Tools: Git, GitHub, Linux, Docker, Postman
        Core CS: Data Structures & Algorithms, Object-Oriented Programming, DBMS, Computer Networks
        
        PROJECTS
        1. High-Performance REST API & Microservice Backend
        - Developed asynchronous backend services using Python and FastAPI handling 500+ concurrent requests.
        - Designed relational database schema using PostgreSQL and SQLAlchemy with connection pooling.
        - Implemented JWT authentication and role-based access control with Redis caching.
        
        2. Real-Time Collaborative Web Application
        - Built frontend client using React, TypeScript, and HTML5 Canvas with WebSocket support.
        - Handled client-side state synchronization with optimistic UI updates and responsive layout styling.
        
        3. Automated Job Search & Data Analytics Crawler
        - Wrote Python automation scripts using Pandas and BeautifulSoup for extracting tech job keywords.
        """

    try:
        pipeline_output = await orchestrator.run_assessment_pipeline(
            resume_bytes_or_text=content,
            full_name=full_name or "",
            email=email or "",
            phone=phone or "",
            github_handle=github_handle or "",
            leetcode_handle=leetcode_handle or "",
            target_domain=target_domain or "All"
        )
        return {
            "success": True,
            "data": pipeline_output
        }
    except Exception as e:
        print(f"[API] Error in assessment pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tailor")
async def run_tailoring_and_staging(req: TailorRequest):
    """Agent 3 + Agent 4 + Agent 5: Tailors resume in STAR format, generates cover letter, stages via Playwright with HITL gate."""
    try:
        result = await orchestrator.run_tailoring_and_staging_pipeline(
            email=req.email,
            job_id=req.job_id
        )
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        print(f"[API] Error in tailoring and staging pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/applications/confirm")
async def confirm_application(req: ConfirmApplicationRequest):
    """HITL Gate: Human explicitly reviews staged fields and clicks submit."""
    try:
        res = await application_agent.human_confirm_and_submit(
            application_id=req.application_id,
            email=req.email
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/interview/evaluate")
async def evaluate_mock_answer(req: InterviewEvalRequest):
    """Agent 5: Evaluates student's answer with dual scoring (Technical & STAR) and model answer."""
    try:
        feedback = await interview_agent.evaluate_answer(
            question=req.question,
            user_answer=req.user_answer,
            role=req.role,
            target_skills=req.skills
        )
        return {
            "success": True,
            "data": feedback
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

