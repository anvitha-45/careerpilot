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
from server.utils.resume_parser import parse_full_resume, structure_resume_with_gemini
from server.utils.job_extractor import process_job_input, find_jobs_from_public_sources
from server.utils.similarity import calculate_comprehensive_readiness
from server.utils.ai_config import (
    ai_vault,
    verify_ai_connection,
    validate_api_key_format,
    infer_provider_from_key,
    sanitize_log_message
)

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

class AIConfigSaveRequest(BaseModel):
    provider: Optional[str] = "auto"
    api_key: Optional[str] = ""
    model: Optional[str] = ""
    temperature: Optional[float] = 0.3

class AIConfigTestRequest(BaseModel):
    provider: Optional[str] = "auto"
    api_key: Optional[str] = ""
    model: Optional[str] = ""

class CustomJobRequest(BaseModel):
    url: Optional[str] = ""
    raw_text: Optional[str] = ""
    strict_url_check: Optional[bool] = False

class FindJobsAIRequest(BaseModel):
    query: Optional[str] = ""
    domain: Optional[str] = "All"
    skills: Optional[List[str]] = []

class MatchJobRequest(BaseModel):
    email: Optional[str] = ""
    job_id: str
    job: Optional[Dict[str, Any]] = None
    profile: Optional[Dict[str, Any]] = None

@router.get("/health")
async def health_check():
    ai_status = ai_vault.get_public_status()
    return {
        "status": "healthy",
        "service": "CareerPilot",
        "version": "2.0.0",
        "database": "MongoDB" if db.is_connected else "Embedded Local Document Store",
        "ai_provider": ai_status["active_provider"],
        "ai_has_key": ai_status["has_active_key"]
    }

@router.get("/ai/config")
async def get_ai_config():
    """Returns current AI configuration and masked key status. Never exposes raw API keys."""
    return {
        "success": True,
        "config": ai_vault.get_public_status()
    }

@router.post("/ai/config")
async def save_ai_config(req: AIConfigSaveRequest):
    """Validates and stores the user's AI API key in the encrypted runtime vault."""
    prov = (req.provider or "auto").lower().strip()
    clean_key = (req.api_key or "").strip()

    if clean_key:
        target_prov = prov if prov in ("gemini", "groq", "openai") else infer_provider_from_key(clean_key)
        valid_fmt, fmt_msg = validate_api_key_format(target_prov, clean_key)
        if not valid_fmt:
            raise HTTPException(status_code=400, detail=fmt_msg)
        prov = target_prov

    status = ai_vault.set_user_key(
        provider=prov,
        api_key=clean_key,
        model=req.model or "",
        temperature=req.temperature
    )
    return {
        "success": True,
        "message": "AI configuration updated securely.",
        "config": status
    }

@router.post("/ai/test")
async def test_ai_config(req: AIConfigTestRequest):
    """Tests connectivity and validity of the provided or active AI API key."""
    result = await verify_ai_connection(
        provider=req.provider,
        api_key=req.api_key,
        model=req.model
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "AI verification failed."))
    return result

@router.delete("/ai/config")
async def clear_ai_config(provider: Optional[str] = None):
    """Revokes and clears stored user API key(s) from the encrypted runtime vault."""
    status = ai_vault.clear_keys(provider=provider)
    return {
        "success": True,
        "message": "API key cleared from runtime vault.",
        "config": status
    }

@router.get("/jobs")
async def get_jobs(q: Optional[str] = None, domain: Optional[str] = None):
    """Retrieve and search saved job descriptions in CareerPilot's database."""
    jobs = await db.find("jobs")
    if domain and domain.lower() != "all":
        dom_low = domain.lower()
        jobs = [j for j in jobs if dom_low in j.get("domain", "").lower()]
    if q and q.strip():
        q_low = q.strip().lower()
        jobs = [
            j for j in jobs
            if q_low in f"{j.get('title', '')} {j.get('company', '')} {j.get('domain', '')} {' '.join(j.get('required_skills', []))}".lower()
        ]
    return {"jobs": jobs}

@router.post("/jobs/search-ai")
async def search_jobs_with_ai_endpoint(req: FindJobsAIRequest):
    """Step 4 (Option 1 - Find jobs with AI): Uses approved public job source + AI skill matching."""
    try:
        saved_jobs = await db.find("jobs")
        found = await find_jobs_from_public_sources(
            query=req.query or "",
            domain=req.domain or "All",
            candidate_skills=req.skills or [],
            saved_jobs=saved_jobs
        )
        # Persist any newly discovered live jobs into the jobs collection so they can be selected & tailored
        for job in found:
            if job.get("id", "").startswith("live-"):
                await db.update_one("jobs", {"id": job["id"]}, job, upsert=True)
        return {
            "success": True,
            "jobs": found
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=sanitize_log_message(str(e)))

@router.post("/jobs/custom")
async def ingest_custom_job_endpoint(req: CustomJobRequest):
    """
    Step 4 (Option 2 - Use a job link & Option 4 - Paste job description):
    Extracts structured job details from a URL or pasted JD text and saves to DB.
    If a URL cannot be accessed, returns fallback_to_paste=True so the UI prompts pasting JD text.
    """
    try:
        job = await process_job_input(
            url=req.url or "",
            raw_text=req.raw_text or "",
            strict_url_check=bool(req.strict_url_check)
        )
        await db.update_one("jobs", {"id": job["id"]}, job, upsert=True)
        return {
            "success": True,
            "job": job
        }
    except ValueError as ve:
        msg = str(ve)
        if "LINK_INACCESSIBLE:" in msg:
            return {
                "success": False,
                "fallback_to_paste": True,
                "message": msg.replace("LINK_INACCESSIBLE:", "").strip()
            }
        raise HTTPException(status_code=400, detail=msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=sanitize_log_message(str(e)))

@router.post("/jobs/match")
async def match_resume_to_selected_job(req: MatchJobRequest):
    """
    Step 5: Match candidate resume to a specific selected job.
    Identifies matching evidence, missing or unverified skills, readiness score, and next steps.
    """
    job = await db.find_one("jobs", {"id": req.job_id})
    if not job:
        all_jobs = await db.find("jobs")
        job = next((j for j in all_jobs if j.get("id") == req.job_id), None)
    if not job and req.job:
        job = req.job
    if not job:
        raise HTTPException(status_code=404, detail="Selected job not found.")

    profile = None
    if req.email:
        profile = await db.find_one("profiles", {"email": req.email.strip().lower()})
    if not profile and req.profile and (req.profile.get("skills") or req.profile.get("raw_resume_text")):
        profile = req.profile
    if not profile:
        all_profiles = await db.find("profiles")
        if all_profiles:
            profile = all_profiles[-1]

    if not profile:
        raise HTTPException(status_code=400, detail="Please upload or assess your resume first.")

    eval_res = calculate_comprehensive_readiness(
        resume_text=profile.get("raw_resume_text", ""),
        candidate_skills=profile.get("skills", []),
        jd=job,
        leetcode_stats=profile.get("leetcode_stats", {}),
        github_stats=profile.get("github_stats", {}),
        projects=profile.get("projects", []),
        experience=profile.get("experience", [])
    )

    match_report = {
        "job_id": job.get("id"),
        "title": job.get("title"),
        "company": job.get("company"),
        "domain": job.get("domain", "Backend"),
        "location": job.get("location"),
        "readiness_score": eval_res["readiness_score"],
        "matched_skills": eval_res["matched_skills"],
        "missing_skills": eval_res["missing_skills"],
        "unverified_skills": eval_res["unverified_skills"],
        "matching_evidence": eval_res["matching_evidence"],
        "next_steps": eval_res["next_steps"]
    }
    return {
        "success": True,
        "match": match_report,
        "job": job
    }

@router.post("/resume/parse")
async def parse_resume_endpoint(
    resume_file: Optional[UploadFile] = File(None),
    resume_text: Optional[str] = Form(None)
):
    """
    Step 1, 2 & 3:
    Accepts PDF, DOCX, or text resume, extracts raw text using Python libraries,
    and uses Gemini (with deterministic fallback) to structure skills, education,
    experience, projects, and links into structured JSON.
    """
    try:
        content: Any = ""
        filename = ""
        if resume_file:
            filename = resume_file.filename or ""
            content = await resume_file.read()
        elif resume_text and resume_text.strip():
            content = resume_text.strip()
        else:
            raise HTTPException(status_code=400, detail="No resume file (PDF/DOCX) or text provided")

        parsed = await structure_resume_with_gemini(content, filename=filename)
        return {
            "success": True,
            "data": {
                "name": parsed.get("name", ""),
                "email": parsed.get("email", ""),
                "phone": parsed.get("phone", ""),
                "github_handle": parsed.get("github_handle", ""),
                "leetcode_handle": parsed.get("leetcode_handle", ""),
                "linkedin_handle": parsed.get("linkedin_handle", ""),
                "links": parsed.get("links", {}),
                "skills": parsed.get("skills", []),
                "education": parsed.get("education", []),
                "experience": parsed.get("experience", []),
                "projects": parsed.get("projects", []),
                "projects_count": len(parsed.get("projects", [])),
                "structured_by": parsed.get("structured_by", "deterministic_parser")
            }
        }
    except Exception as e:
        print(f"[API] Error parsing resume: {sanitize_log_message(str(e))}")
        raise HTTPException(status_code=500, detail=sanitize_log_message(str(e)))

@router.post("/assess")
async def run_assessment(
    resume_file: Optional[UploadFile] = File(None),
    resume_text: Optional[str] = Form(None),
    full_name: Optional[str] = Form(""),
    email: Optional[str] = Form(""),
    phone: Optional[str] = Form(""),
    github_handle: Optional[str] = Form(""),
    leetcode_handle: Optional[str] = Form(""),
    target_domain: Optional[str] = Form("All"),
    selected_job_id: Optional[str] = Form("")
):
    """Agent 1 + Agent 2: Ingests PDF/DOCX resume, structures candidate info with Gemini, and matches to selected job."""
    content: Any = ""
    filename = ""
    if resume_file:
        filename = resume_file.filename or ""
        content = await resume_file.read()
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
            target_domain=target_domain or "All",
            filename=filename,
            selected_job_id=selected_job_id or ""
        )
        return {
            "success": True,
            "data": pipeline_output
        }
    except Exception as e:
        print(f"[API] Error in assessment pipeline: {sanitize_log_message(str(e))}")
        raise HTTPException(status_code=500, detail=sanitize_log_message(str(e)))

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

