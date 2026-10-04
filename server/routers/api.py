import json
import hashlib
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from server.database import db
from server.agents.orchestrator import orchestrator
from server.agents.application_agent import application_agent
from server.agents.interview_agent import interview_agent
from server.utils.resume_parser import parse_full_resume
from server.utils.job_extractor import process_job_input
from server.utils.similarity import calculate_comprehensive_readiness

router = APIRouter(prefix="/api", tags=["Pipeline API"])

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

class AuthRegisterRequest(BaseModel):
    username: str
    password: str
    name: Optional[str] = ""
    email: Optional[str] = ""

class AuthLoginRequest(BaseModel):
    username: str
    password: str

class SaveProfileRequest(BaseModel):
    username: str
    email: str
    name: Optional[str] = ""
    phone: Optional[str] = ""
    github_handle: Optional[str] = ""
    leetcode_handle: Optional[str] = ""
    linkedin_handle: Optional[str] = ""
    skills: Optional[List[str]] = []
    target_domain: Optional[str] = "All"

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

class AnalyzeCustomJobRequest(BaseModel):
    url: Optional[str] = ""
    raw_text: Optional[str] = ""
    email: Optional[str] = ""

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

@router.post("/jobs/analyze-custom")
async def analyze_custom_job(req: AnalyzeCustomJobRequest):
    """
    Ingests an external job posting URL or pasted text, extracts structured requirements,
    saves it to the database, and computes candidate readiness match.
    """
    try:
        url = (req.url or "").strip()
        raw_text = (req.raw_text or "").strip()
        if not url and not raw_text:
            raise HTTPException(status_code=400, detail="Please provide a job posting URL or job description text.")

        job_doc = await process_job_input(url=url, raw_text=raw_text)

        # Upsert into database so it becomes immediately available across all agents and tabs
        await db.update_one("jobs", {"id": job_doc["id"]}, job_doc, upsert=True)

        # Look up candidate profile for instant match scoring
        profile = None
        if req.email:
            profile = await db.find_one("profiles", {"email": req.email.strip().lower()})
        if not profile:
            all_profiles = await db.find("profiles")
            if all_profiles:
                profile = all_profiles[-1]

        if not profile:
            profile = {
                "raw_resume_text": "Python FastAPI PostgreSQL Docker Git React",
                "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Git", "REST APIs"],
                "leetcode_stats": {"total_solved": 120},
                "github_stats": {"public_repos": 8, "total_stars": 3}
            }

        eval_res = calculate_comprehensive_readiness(
            resume_text=profile.get("raw_resume_text", ""),
            candidate_skills=profile.get("skills", []),
            jd=job_doc,
            leetcode_stats=profile.get("leetcode_stats", {}),
            github_stats=profile.get("github_stats", {})
        )

        return {
            "success": True,
            "message": f"Successfully analyzed job posting: {job_doc['company']} - {job_doc['title']}",
            "job": job_doc,
            "readiness": {
                "readiness_score": eval_res["readiness_score"],
                "matched_skills": eval_res["matched_skills"],
                "missing_skills": eval_res["missing_skills"]
            }
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"[API] Error analyzing custom job: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze job posting: {str(e)}")

@router.post("/resume/parse")
async def parse_resume_endpoint(
    resume_file: Optional[UploadFile] = File(None),
    resume_text: Optional[str] = Form(None)
):
    """
    Instantly extracts candidate name, contact info, GitHub, LeetCode, LinkedIn,
    and skills from uploaded resume file or text.
    """
    try:
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
            raise HTTPException(status_code=400, detail="No resume file or text provided")

        parsed = parse_full_resume(content)
        return {
            "success": True,
            "data": {
                "name": parsed.get("name", ""),
                "email": parsed.get("email", ""),
                "phone": parsed.get("phone", ""),
                "github_handle": parsed.get("github_handle", ""),
                "leetcode_handle": parsed.get("leetcode_handle", ""),
                "linkedin_handle": parsed.get("linkedin_handle", ""),
                "skills": parsed.get("skills", []),
                "projects_count": len(parsed.get("projects", []))
            }
        }
    except Exception as e:
        print(f"[API] Error parsing resume: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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

@router.get("/applications")
async def get_applications(email: Optional[str] = None):
    """Retrieve list of candidate's submitted / staged applications for the tracking dashboard."""
    apps = await db.find("applications")
    if email:
        target = email.lower().strip()
        apps = [a for a in apps if a.get("email", "").lower().strip() == target]
    return {"applications": apps}

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

@router.post("/auth/register")
async def register_user(req: AuthRegisterRequest):
    """Registers a new user account with username and password."""
    username = req.username.strip()
    password = req.password.strip()
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password are required.")
    
    if len(password) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters long.")

    # Check if username already exists
    existing = await db.find_one("users", {"username": username})
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists. Please choose another or log in.")

    email = (req.email or "").strip().lower()
    if email:
        existing_email = await db.find_one("users", {"email": email})
        if existing_email:
            raise HTTPException(status_code=400, detail="An account with this email already exists. Please log in.")

    name = req.name.strip() if req.name and req.name.strip() else username
    user_doc = {
        "username": username,
        "name": name,
        "email": email,
        "password_hash": hash_password(password),
        "created_at": datetime.utcnow().isoformat()
    }
    await db.insert("users", user_doc)
    
    return {
        "success": True,
        "message": "Account created successfully.",
        "user": {
            "username": username,
            "name": name,
            "email": email
        }
    }

@router.post("/auth/login")
async def login_user(req: AuthLoginRequest):
    """Authenticates an existing user via username/email and password."""
    identifier = req.username.strip()
    password = req.password.strip()
    if not identifier or not password:
        raise HTTPException(status_code=400, detail="Username/email and password are required.")

    # Search by username or email
    user = await db.find_one("users", {"username": identifier})
    if not user and "@" in identifier:
        user = await db.find_one("users", {"email": identifier.lower()})

    if not user:
        raise HTTPException(status_code=401, detail="Account not found. Please check your credentials or create an account.")

    # Verify password hash
    expected_hash = user.get("password_hash")
    if expected_hash and expected_hash != hash_password(password):
        if user.get("password") != password:
            raise HTTPException(status_code=401, detail="Incorrect password. Please try again.")

    return {
        "success": True,
        "message": "Logged in successfully.",
        "user": {
            "username": user["username"],
            "name": user.get("name", user["username"]),
            "email": user.get("email", "")
        }
    }

@router.post("/profile/save")
async def save_profile_endpoint(req: SaveProfileRequest):
    """Saves candidate profile to their account in the database. Requires login."""
    username = req.username.strip()
    if not username or username.lower() == "guest":
        raise HTTPException(status_code=401, detail="To save your information, you must log in or create an account.")

    email = (req.email or "").strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="A valid email address is required to save your profile.")

    profile_data = {
        "username": username,
        "name": req.name.strip() if req.name else username,
        "email": email,
        "phone": req.phone.strip() if req.phone else "",
        "github_handle": req.github_handle.strip() if req.github_handle else "",
        "leetcode_handle": req.leetcode_handle.strip() if req.leetcode_handle else "",
        "linkedin_handle": req.linkedin_handle.strip() if req.linkedin_handle else "",
        "skills": req.skills or [],
        "target_domain": req.target_domain or "All",
        "updated_at": datetime.utcnow().isoformat()
    }

    await db.update_one("profiles", {"email": email}, profile_data, upsert=True)
    await db.update_one("users", {"username": username}, {
        "name": profile_data["name"],
        "email": email,
        "phone": profile_data["phone"]
    }, upsert=False)

    return {
        "success": True,
        "message": "Profile saved successfully.",
        "profile": profile_data
    }

@router.get("/profile")
async def get_profile_endpoint(email: Optional[str] = None, username: Optional[str] = None):
    """Retrieves saved profile for a user."""
    query = {}
    if email:
        query["email"] = email.strip().lower()
    elif username:
        query["username"] = username.strip()
    else:
        raise HTTPException(status_code=400, detail="Email or username is required.")

    profile = await db.find_one("profiles", query)
    if not profile and username:
        user = await db.find_one("users", {"username": username})
        if user:
            return {
                "success": True,
                "profile": {
                    "username": user["username"],
                    "name": user.get("name", user["username"]),
                    "email": user.get("email", ""),
                    "phone": user.get("phone", ""),
                    "github_handle": "",
                    "leetcode_handle": "",
                    "skills": [],
                    "target_domain": "All"
                }
            }

    return {"success": True, "profile": profile}

