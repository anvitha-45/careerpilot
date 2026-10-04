import asyncio
import os
import sys

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server.database import db
from server.utils.job_extractor import process_job_input
from server.utils.similarity import calculate_comprehensive_readiness

SAMPLE_CUSTOM_JD = """
Company: Cred Tech
Role: Backend Software Development Engineer (SDE-1)
Location: Bengaluru, India (Hybrid)
We are looking for a Backend Engineer to build scalable payment microservices.
Key Responsibilities:
- Design high-throughput REST APIs using Python, FastAPI or Go.
- Optimize database queries with PostgreSQL and Redis.
- Deploy containerized services using Docker and Kubernetes on AWS.
Required Qualifications:
- 0 to 2 years of software engineering experience.
- Strong proficiency in Python, PostgreSQL, Git, Docker, and REST APIs.
- Preferred knowledge of Kafka, Redis, and Microservices.
"""

async def test_custom_job_analysis():
    print("=" * 60)
    print("TESTING CUSTOM JOB LINK & TEXT INGESTION")
    print("=" * 60)

    await db.initialize()

    # 1. Test parsing raw text
    print("\n[Step 1] Parsing custom job posting text...")
    job = await process_job_input(raw_text=SAMPLE_CUSTOM_JD, url="https://careers.cred.club/jobs/backend-sde1")
    print(f"-> Extracted Company: {job['company']}")
    print(f"-> Extracted Title: {job['title']}")
    print(f"-> Inferred Domain: {job['domain']}")
    print(f"-> Required Skills: {job['required_skills']}")
    print(f"-> Portal URL: {job['portal_url']}")
    print(f"-> LinkedIn Search URL: {job['apply_search_url']}")

    assert job["company"] != "", "Company should not be empty"
    assert job["title"] != "", "Title should not be empty"
    assert len(job["required_skills"]) > 0, "Should detect required skills"

    # 2. Test upserting into database
    print("\n[Step 2] Upserting custom job into database...")
    await db.update_one("jobs", {"id": job["id"]}, job, upsert=True)
    saved_job = await db.find_one("jobs", {"id": job["id"]})
    assert saved_job is not None, "Job should be persisted in DB"
    assert saved_job["id"] == job["id"], "Job ID should match"
    print("-> Successfully persisted custom job in database.")

    # 3. Test readiness calculation against candidate profile
    print("\n[Step 3] Calculating candidate match & readiness score...")
    mock_profile = {
        "raw_resume_text": "Experienced in Python, FastAPI, PostgreSQL, Docker, Git, building REST APIs.",
        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Git", "REST APIs"],
        "leetcode_stats": {"total_solved": 150},
        "github_stats": {"public_repos": 10, "total_stars": 5}
    }

    readiness = calculate_comprehensive_readiness(
        resume_text=mock_profile["raw_resume_text"],
        candidate_skills=mock_profile["skills"],
        jd=saved_job,
        leetcode_stats=mock_profile["leetcode_stats"],
        github_stats=mock_profile["github_stats"]
    )
    print(f"-> Match Readiness Score: {readiness['readiness_score']}%")
    print(f"-> Matched Skills: {readiness['matched_skills']}")
    print(f"-> Missing Skills: {readiness['missing_skills']}")

    assert readiness["readiness_score"] >= 50, "Readiness score should be substantial given skill overlap"
    print("\nALL CUSTOM JOB TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(test_custom_job_analysis())
