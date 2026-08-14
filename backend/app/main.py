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

async def launch_browser_task(target_url: str):
    async with async_playwright() as playwright_instance:
        browser_session = await playwright_instance.chromium.launch(headless=False)
        active_page = await browser_session.new_page()
        await active_page.goto(target_url)
        await asyncio.sleep(60)

@app.post("/api/run-pipeline")
async def run_pipeline(
    resume_file: UploadFile = File(...),
    jd_text: str = Form(...),
    jd_url: str = Form(...)
):
    document_bytes = await resume_file.read()
    document_filename = resume_file.filename.lower()
    extracted_resume_text = ""

    if document_filename.endswith(".pdf"):
        pdf_reader = PdfReader(io.BytesIO(document_bytes))
        for page in pdf_reader.pages:
            extracted_page_text = page.extract_text()
            if extracted_page_text:
                extracted_resume_text += extracted_page_text + "\n"
    elif document_filename.endswith(".docx"):
        word_document = Document(io.BytesIO(document_bytes))
        for paragraph in word_document.paragraphs:
            extracted_resume_text += paragraph.text + "\n"
    else:
        extracted_resume_text = document_bytes.decode("utf-8", errors="ignore")

    print(f"\n--- PARSED DOCUMENT: {document_filename} ---")
    
    initial_pipeline_state = {
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
        pipeline_result = await applicationWorkflow.ainvoke(initial_pipeline_state)
    except Exception as error:
        print(f"\nCRITICAL ERROR: {str(error)}\n")
        pipeline_result = initial_pipeline_state
        pipeline_result["tailoredBullets"] = [f"⚠️ PIPELINE CRASHED: {str(error)}"]
    
    tailored_output_materials = pipeline_result.get("tailoredBullets", [])
    generated_cover_letter = pipeline_result.get("coverLetter", "")
    
    if generated_cover_letter:
        tailored_output_materials.append(f"\n--- Generated Cover Letter ---\n{generated_cover_letter}")
        
    mock_interview_questions = pipeline_result.get("interviewQuestions", [])
    if mock_interview_questions:
        tailored_output_materials.append(f"\n--- Mock Interview Questions ---\n" + "\n".join([f"• {question}" for question in mock_interview_questions]))
    
    return {
        "extracted_skills": pipeline_result.get("candidateSkills", []),
        "missing_skills": pipeline_result.get("missingSkills", []),
        "tailored_bullets": tailored_output_materials,
        "ats_score": pipeline_result.get("atsScore", 0)
    }

@app.post("/api/stage-application")
async def stage_application(payload: dict, background_tasks: BackgroundTasks):
    destination_url = payload.get("url") or "https://google.com"
    if not destination_url.startswith(("http://", "https://")):
        destination_url = "https://" + destination_url

    background_tasks.add_task(launch_browser_task, destination_url)
    return {"status": "Browser launching in background!"}