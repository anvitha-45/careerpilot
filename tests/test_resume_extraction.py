import os
import sys

# Ensure root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server.utils.resume_parser import (
    parse_contact_info,
    parse_full_resume,
    extract_raw_text_from_file,
    structure_resume_with_gemini,
)
from server.agents.orchestrator import orchestrator
import asyncio
import io
import zipfile


def test_docx_and_5step_assessment():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(
            "word/document.xml",
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            "<w:body><w:p><w:r><w:t>"
            "Priya Sundaram | priya.sundaram@vit.ac.in | github.com/priya-codes | "
            "B.Tech Computer Science 2026 | Skills: Python, FastAPI, Docker, React, SQL | "
            "Project: Cloud Task Queue built with Python and FastAPI"
            "</w:t></w:r></w:p></w:body></w:document>",
        )
    docx_bytes = buf.getvalue()
    raw_text = extract_raw_text_from_file(docx_bytes, "Priya_Resume.docx")
    assert "Priya Sundaram" in raw_text

    structured = asyncio.run(
        structure_resume_with_gemini(docx_bytes, filename="Priya_Resume.docx")
    )
    assert "skills" in structured and "education" in structured and "experience" in structured
    assert "projects" in structured and "links" in structured

    result = asyncio.run(
        orchestrator.run_assessment_pipeline(
            resume_bytes_or_text=docx_bytes,
            filename="Priya_Resume.docx",
        )
    )
    profile = result["profile"]
    match = profile["selected_job_match"]
    assert "matching_evidence" in match
    assert "missing_skills" in match
    assert "unverified_skills" in match
    assert "readiness_score" in match
    assert "next_steps" in match
    print("5-STEP ASSESSMENT & DOCX TESTS PASSED!")


def test_auto_extraction():
    sample_text = """
    PRIYA SUNDARAM
    priya.sundaram@vit.ac.in | +91 9845012345 | Chennai, India
    GitHub: https://github.com/priya-codes | LeetCode: https://leetcode.com/u/priya_algo | LinkedIn: linkedin.com/in/priya-sundaram

    EDUCATION
    B.Tech Computer Science & Engineering (2022 - 2026) - CGPA: 9.1/10

    SKILLS
    Python, FastAPI, Docker, PostgreSQL, React, Git, Redis

    PROJECTS
    1. Distributed Cloud Task Queue
    - Built task scheduling service with Redis and Celery handling 1,000 tasks/min.
    """

    contact = parse_contact_info(sample_text)
    print("Parsed Contact:", contact)

    assert contact["name"] == "Priya Sundaram", f"Expected 'Priya Sundaram', got '{contact['name']}'"
    assert contact["email"] == "priya.sundaram@vit.ac.in", f"Expected email, got '{contact['email']}'"
    assert "9845012345" in contact["phone"], f"Expected phone with 9845012345, got '{contact['phone']}'"
    assert contact["github_handle"] == "priya-codes", f"Expected 'priya-codes', got '{contact['github_handle']}'"
    assert contact["leetcode_handle"] == "priya_algo", f"Expected 'priya_algo', got '{contact['leetcode_handle']}'"
    assert contact["linkedin_handle"] == "priya-sundaram", f"Expected 'priya-sundaram', got '{contact['linkedin_handle']}'"

    full = parse_full_resume(sample_text)
    assert len(full["skills"]) >= 5, f"Expected at least 5 skills, got {len(full['skills'])}"
    assert full["github_handle"] == "priya-codes"
    assert full["leetcode_handle"] == "priya_algo"

    print("ALL RESUME EXTRACTION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_auto_extraction()
    test_docx_and_5step_assessment()
