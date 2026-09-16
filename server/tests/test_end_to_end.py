import asyncio
import os
import sys

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from server.config import settings
from server.database import db_manager, get_users_col, get_jobs_col
from server.seeds.seed_data import seed_initial_jobs
from server.agents.assessment_agent import assessment_agent
from server.agents.gap_learning_agent import gap_learning_agent
from server.agents.tailoring_agent import tailoring_agent
from server.agents.application_agent import application_agent
from server.agents.interview_agent import interview_agent
from server.services.vector_service import vector_service

async def run_all_tests():
    print("======================================================================")
    print("             CareerPilot AI — End-to-End System Verification")
    print("======================================================================")

    # 1. Database & Seeding Check
    print("\n[Test 1] Initializing Hybrid Database & Seeding...")
    db_manager.initialize()
    await seed_initial_jobs()
    jobs_col = get_jobs_col()
    jobs = await jobs_col.find({})
    assert len(jobs) >= 5, f"Expected at least 5 seeded jobs, got {len(jobs)}"
    print(f"[PASS] Database active ({'MongoDB' if db_manager.is_mongo else 'Embedded Local Store'}), {len(jobs)} jobs verified.")

    # 2. Assessment Agent Test
    print("\n[Test 2] Testing Assessment Agent (Resume NLP + Signal Extraction)...")
    sample_resume = """
    Aarav Sharma
    Email: aarav@example.com | Phone: +91 9876543210
    Education: B.Tech Computer Science (2026 Batch)
    Technical Skills: Python, FastAPI, React, SQL, PostgreSQL, Git, Docker, Data Structures, Algorithms, OOP.
    Projects: Built a Distributed Task Queue with asynchronous API workers.
    """
    assessment_res = await assessment_agent.run(
        resume_text=sample_resume,
        github_username="testdev",
        leetcode_username="testlc",
        target_roles=["Software Engineer", "Backend Developer"]
    )
    skills = assessment_res["skill_vector"]["all_skills"]
    assert "Python" in skills and "FastAPI" in skills, "Expected Python and FastAPI in extracted skills"
    assert assessment_res["readiness_score"] > 50, "Expected readiness score > 50"
    print(f"[PASS] Assessment Agent extracted {len(skills)} skills. Candidate Readiness: {assessment_res['readiness_score']}%")

    # 3. Semantic Matching & Vector Engine
    print("\n[Test 3] Testing Semantic Vector Matching...")
    target_job = jobs[0]
    match_res = vector_service.compute_match(
        candidate_skills=skills,
        required_skills=target_job.get("required_skills", []),
        preferred_skills=target_job.get("preferred_skills", []),
        candidate_target_roles=["Software Engineer"],
        job_title=target_job.get("title", ""),
        candidate_location="India",
        job_location=target_job.get("location", "")
    )
    assert 0 <= match_res["match_score"] <= 100, "Match score out of range"
    print(f"[PASS] Vector Match against '{target_job['title']}': {match_res['match_score']}% Match. Explanation: {match_res['explanation'][:60]}...")

    # 4. Gap & Learning Agent
    print("\n[Test 4] Testing Gap & Learning Agent (Market Frequency Scoring)...")
    gap_res = await gap_learning_agent.run(
        user_id="test_user_123",
        candidate_skills=skills,
        target_roles=["Software Engineer"]
    )
    assert "gaps" in gap_res and len(gap_res["gaps"]) > 0, "Expected market gaps"
    assert "weeks" in gap_res and len(gap_res["weeks"]) == 4, "Expected 4-week roadmap"
    top_gap = gap_res["gaps"][0]
    print(f"[PASS] Top Market Gap Identified: {top_gap['skill']} ({top_gap['frequency_percentage']}% of JDs). Curated Resources: {len(top_gap['resources'])}")

    # 5. Tailoring Agent (CAR/STAR + 0% Hallucination)
    print("\n[Test 5] Testing Tailoring Agent (STAR Bullets & Zero-Hallucination Diff)...")
    candidate_profile = {
        "full_name": "Aarav Sharma",
        "skill_vector": assessment_res["skill_vector"]
    }
    tailor_res = await tailoring_agent.run(
        candidate_profile=candidate_profile,
        job=target_job
    )
    assert tailor_res["zero_hallucination_verified"] is True, "Expected zero-hallucination verification"
    assert len(tailor_res["bullet_rewrites"]) >= 2, "Expected tailored bullet rewrites"
    print(f"[PASS] Tailored {len(tailor_res['bullet_rewrites'])} bullets using CAR/STAR. Verified zero hallucination across {tailor_res['verified_terms_count']} terms.")

    # 6. Application Agent (Playwright Browser Staging & HITL Gate)
    print("\n[Test 6] Testing Application Agent & Mandatory Human Review Gate...")
    stage_res = await application_agent.stage_application(
        user_id="test_user_123",
        job=target_job,
        candidate_profile=candidate_profile,
        tailored_resume_filename="tailored_aarav_swiggy.pdf"
    )
    assert stage_res["status"] == "READY_FOR_REVIEW", f"Expected READY_FOR_REVIEW, got {stage_res['status']}"
    assert len(stage_res["staging_session"]["staged_fields"]) >= 5, "Expected staged form fields"
    print(f"[PASS] Staging complete. Status is '{stage_res['status']}'. Browser session halted at Human Review Gate (ToS Safe).")

    # Confirm application (simulating candidate human action)
    confirm_res = await application_agent.confirm_submission(
        user_id="test_user_123",
        application_id=stage_res["id"]
    )
    assert confirm_res["status"] == "USER_SUBMITTED", "Expected USER_SUBMITTED after manual confirmation"
    print(f"[PASS] Candidate confirmed review: Status transitioned to '{confirm_res['status']}'.")

    # 7. Interview Prep Agent
    print("\n[Test 7] Testing Interview Prep Agent (JD-Specific Q&A & Evaluation)...")
    questions = await interview_agent.generate_questions_for_job(target_job)
    assert len(questions) >= 3, "Expected at least 3 interview questions"
    
    # Simulate candidate answers
    mock_answers = {
        questions[0]["id"]: "In high concurrency scenarios, I use Optimistic Locking with version columns, and fallback to Redis distributed locks with TTLs to prevent deadlocks.",
        questions[1]["id"]: "We chose Redis over in-memory caching to allow stateless horizontal scaling, accepting a 2ms network hop for scalability."
    }
    eval_res = await interview_agent.evaluate_answers(questions, mock_answers)
    assert 0 <= eval_res["overall_score"] <= 100, "Interview score out of range"
    print(f"[PASS] Interview Evaluation Complete. Score: {eval_res['overall_score']}/100 ({eval_res['readiness_level']}).")

    print("\n======================================================================")
    print(" [SUCCESS] ALL 7 END-TO-END AGENT & PIPELINE TESTS PASSED WITH 100% SUCCESS!")
    print("======================================================================")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
