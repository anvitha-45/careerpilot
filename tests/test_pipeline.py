import asyncio
import os
import sys

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server.database import db
from server.seeds.seed_data import seed_initial_jobs
from server.agents.assessment_agent import assessment_agent
from server.agents.gap_learning_agent import gap_learning_agent
from server.agents.tailoring_agent import tailoring_agent
from server.agents.application_agent import application_agent
from server.agents.interview_agent import interview_agent

SAMPLE_RESUME = """
ANANYA SHARMA
Email: ananya.sharma@example.com | Phone: +91 9876543210
GitHub: github.com/ananya-dev | LinkedIn: linkedin.com/in/ananya-sharma

EDUCATION
B.Tech in Computer Science and Engineering (2022 - 2026)
CGPA: 8.7/10

TECHNICAL SKILLS
Languages: Python, JavaScript, SQL, HTML5, CSS3
Frameworks: FastAPI, Flask, React.js
Databases: PostgreSQL, SQLite
Tools: Git, GitHub, Linux, Docker (Basics), Postman
Core CS: Data Structures & Algorithms, Object-Oriented Programming, DBMS, Computer Networks

PROJECTS
1. E-Commerce Order Management Microservice
- Developed asynchronous backend service with Python and FastAPI handling 200+ concurrent requests.
- Designed relational database schema using PostgreSQL and SQLAlchemy ORM.
- Implemented JWT authentication and role-based access control.

2. Real-Time Collaborative Whiteboard
- Built frontend using React and HTML5 Canvas with WebSocket support.
- Handled state synchronization across multiple connected browser clients.
"""

async def run_e2e_test():
    print("=" * 60)
    print("RUNNING CAREERPILOT MULTI-AGENT E2E TEST")
    print("=" * 60)

    # 1. Initialize DB and Seeds
    print("\n[Step 1] Initializing Database & Seeding Jobs...")
    await db.initialize()
    await seed_initial_jobs()
    jobs = await db.find("jobs")
    assert len(jobs) > 0, "Jobs collection should have seeded records"
    print(f"-> Seeded {len(jobs)} jobs successfully.")

    # 2. Agent 1: Assessment
    print("\n[Step 2] Executing Agent 1: Assessment Agent...")
    profile = await assessment_agent.execute(
        resume_bytes_or_text=SAMPLE_RESUME,
        github_handle="ananya-dev",
        leetcode_handle="ananya_codes",
        target_domain="Backend"
    )
    assert profile["overall_readiness_score"] > 0
    assert len(profile["skills"]) > 0
    print(f"-> Candidate: {profile['name']}")
    print(f"-> Overall Readiness: {profile['overall_readiness_score']}%")
    print(f"-> Verified Skills ({len(profile['skills'])}): {', '.join(profile['skills'][:6])}...")

    # 3. Agent 2: Gap & Learning
    print("\n[Step 3] Executing Agent 2: Gap & Learning Agent...")
    gaps_result = await gap_learning_agent.execute(profile)
    ranked_gaps = gaps_result["ranked_gaps"]
    assert len(ranked_gaps) > 0
    print(f"-> Found {len(ranked_gaps)} missing skill gaps.")
    print(f"-> Top missing gap: {ranked_gaps[0]['skill']} ({ranked_gaps[0]['market_demand_percentage']}% demand)")
    if ranked_gaps[0]["resources"]:
        print(f"-> Curated Free Resource: {ranked_gaps[0]['resources'][0]['title']} ({ranked_gaps[0]['resources'][0]['platform']})")

    # 4. Agent 3: Tailoring
    print("\n[Step 4] Executing Agent 3: Tailoring Agent...")
    target_job = jobs[0]
    tailored_out = await tailoring_agent.execute(profile, target_job)
    assert len(tailored_out["tailored_bullets"]) > 0
    assert len(tailored_out["cover_letter"]) > 50
    print(f"-> Tailored for: {target_job['title']} at {target_job['company']}")
    print(f"-> STAR Bullet Sample: {tailored_out['tailored_bullets'][0]['star_tailored_bullet']}")
    print(f"-> Cover letter length: {len(tailored_out['cover_letter'])} chars")

    # 5. Agent 4: Application Staging (HITL Checkpoint)
    print("\n[Step 5] Executing Agent 4: Application Staging Agent (HITL Gate)...")
    staged_payload = await application_agent.stage_application(profile, target_job, tailored_out)
    assert staged_payload["status"] == "STAGED_AWAITING_APPROVAL"
    print(f"-> Staging status: {staged_payload['status']}")
    print(f"-> Staged fields count: {len(staged_payload['staged_fields'])}")
    print(f"-> HITL Compliance notice: {staged_payload['compliance_notice'][:65]}...")

    # Test Human Confirmation
    confirm_res = await application_agent.human_confirm_and_submit(
        application_id=staged_payload["application_id"],
        email=profile["email"]
    )
    assert confirm_res["status"] == "APPROVED_BY_HUMAN_SUBMITTED"
    print(f"-> Human confirmed status: {confirm_res['status']}")

    # 6. Agent 5: Interview Prep Agent
    print("\n[Step 6] Executing Agent 5: Interview Prep Agent...")
    questions = await interview_agent.generate_questions(target_job, profile)
    assert len(questions) > 0
    print(f"-> Generated {len(questions)} interview questions.")
    sample_q = questions[0]
    print(f"-> Sample Question: {sample_q['question']}")

    # Test Answer Evaluation
    eval_res = await interview_agent.evaluate_answer(
        question=sample_q["question"],
        user_answer="In my project, I implemented async worker queues using Celery and Redis to handle peak loads. When requests surged to 500/sec, response latency remained under 120ms.",
        role=target_job["title"],
        target_skills=target_job["required_skills"]
    )
    assert eval_res["technical_score"] >= 1
    assert eval_res["communication_score"] >= 1
    print(f"-> Evaluation: Technical {eval_res['technical_score']}/10, Comm {eval_res['communication_score']}/10")
    print(f"-> Feedback: {eval_res['feedback'][:70]}...")

    print("\n" + "=" * 60)
    print("ALL 5 AGENTS & HITL GATE PASSED VERIFICATION!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_e2e_test())
