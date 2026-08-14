from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from app.workflow import applicationWorkflow
from playwright.async_api import async_playwright
import asyncio
import io
from pypdf import PdfReader
from docx import Document

app = FastAPI(title="CareerPilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def launch_browser_task(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(url)
        await asyncio.sleep(60)

@app.post("/api/run-pipeline")
async def run_pipeline(
    resume_file: UploadFile = File(...),
    jd_text: str = Form(...),
    jd_url: str = Form(...)
):
    document_bytes = await resume_file.read()
    filename = resume_file.filename.lower()
    extracted_resume_text = ""

    if filename.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(document_bytes))
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                extracted_resume_text += extracted + "\n"
    elif filename.endswith(".docx"):
        doc = Document(io.BytesIO(document_bytes))
        for paragraph in doc.paragraphs:
            extracted_resume_text += paragraph.text + "\n"
    else:
        extracted_resume_text = document_bytes.decode("utf-8", errors="ignore")

    print(f"\n--- PARSED DOCUMENT: {filename} ---")
    
    initial_state = {
        "resumeText": extracted_resume_text,
        "jobDescription": jd_text,
        "targetUrl": jd_url,
        "candidateSkills": [],
        "missingSkills": [],
        "learningResources": [],
        "tailoredBullets": [],
        "coverLetter": "",
        "interviewQuestions": [],
        "isApplicationStaged": False
    }
    
    try:
        pipeline_result = await applicationWorkflow.ainvoke(initial_state)
    except Exception as error:
        print(f"\nCRITICAL ERROR: {str(error)}\n")
        pipeline_result = initial_state
        pipeline_result["tailoredBullets"] = [f"⚠️ PIPELINE CRASHED: {str(error)}"]
    
    tailored_output = pipeline_result.get("tailoredBullets", [])
    cover_letter = pipeline_result.get("coverLetter", "")
    
    if cover_letter:
        tailored_output.append(f"\n--- Generated Cover Letter ---\n{cover_letter}")
        
    interview_questions = pipeline_result.get("interviewQuestions", [])
    if interview_questions:
        tailored_output.append(f"\n--- Mock Interview Questions ---\n" + "\n".join([f"• {q}" for q in interview_questions]))
    
    return {
        "extracted_skills": pipeline_result.get("candidateSkills", []),
        "missing_skills": pipeline_result.get("missingSkills", []),
        "tailored_bullets": tailored_output
    }

@app.post("/api/stage-application")
async def stage_application(payload: dict, background_tasks: BackgroundTasks):
    target_url = payload.get("url") or "https://google.com"
    if not target_url.startswith(("http://", "https://")):
        target_url = "https://" + target_url

    background_tasks.add_task(launch_browser_task, target_url)
    return {"status": "Browser launching in background!"}