import asyncio
from typing import Dict, Any, List, Optional
from server.utils.resume_parser import structure_resume_with_gemini
from server.utils.github_client import fetch_github_profile
from server.utils.leetcode_client import fetch_leetcode_profile
from server.utils.similarity import calculate_comprehensive_readiness, analyze_skill_evidence
from server.database import db

class AssessmentAgent:
    """
    Agent 1: Multi-Step Candidate Assessment Agent.
    1. Ingests uploaded PDF or DOCX resume.
    2. Extracts raw text using Python libraries.
    3. Uses Gemini (with deterministic fallback) to structure skills, education, experience, projects, and links into JSON.
    4. Validates public profiles (GitHub/LeetCode).
    5. Matches the resume against the user's selected job (and benchmark postings) to identify matching evidence,
       missing or unverified skills, readiness score, and actionable next steps.
    """

    def __init__(self):
        self.name = "Assessment Agent"

    async def execute(
        self,
        resume_bytes_or_text: Any,
        full_name: str = "",
        email: str = "",
        phone: str = "",
        github_handle: str = "",
        leetcode_handle: str = "",
        target_domain: str = "Backend",
        filename: str = "",
        selected_job_id: str = ""
    ) -> Dict[str, Any]:
        print(f"[{self.name}] Initiating 5-step candidate assessment & job matching...")

        # Step 2 & Step 3: Extract raw text from PDF/DOCX and structure with Gemini into JSON
        parsed_resume = await structure_resume_with_gemini(resume_bytes_or_text, filename=filename)

        # Override handles & contact info if candidate provided in input form
        cand_name = full_name.strip() or parsed_resume.get("name") or "Candidate"
        cand_email = email.strip() or parsed_resume.get("email") or "candidate@example.com"
        cand_phone = phone.strip() or parsed_resume.get("phone") or "+91 9876543210"
        gh_user = github_handle.strip() or parsed_resume.get("github_handle", "")
        lc_user = leetcode_handle.strip() or parsed_resume.get("leetcode_handle", "")
        li_user = parsed_resume.get("linkedin_handle", "")

        # Concurrently fetch verified signals from GitHub and LeetCode
        gh_task = fetch_github_profile(gh_user) if gh_user else asyncio.sleep(0, result={})
        lc_task = fetch_leetcode_profile(lc_user) if lc_user else asyncio.sleep(0, result={})
        github_stats, leetcode_stats = await asyncio.gather(gh_task, lc_task)

        # Merge extracted resume skills with languages verified in GitHub
        all_skills = set(parsed_resume.get("skills", []))
        if github_stats.get("top_languages"):
            for lang in github_stats["top_languages"]:
                all_skills.add(lang)
        verified_skills = sorted(list(all_skills))

        # Audit which candidate skills have concrete project/experience/GitHub evidence vs unverified
        skill_verification_map: List[Dict[str, Any]] = []
        candidate_unverified_skills: List[str] = []
        for sk in verified_skills:
            has_ev, ev_sources = analyze_skill_evidence(
                skill=sk,
                projects=parsed_resume.get("projects", []),
                experience=parsed_resume.get("experience", []),
                github_stats=github_stats,
                leetcode_stats=leetcode_stats
            )
            skill_verification_map.append({
                "skill": sk,
                "verified": has_ev,
                "evidence": ev_sources if has_ev else ["Listed in skills section without project/GitHub proof"]
            })
            if not has_ev:
                candidate_unverified_skills.append(sk)

        # Retrieve target JDs from database
        all_jds = await db.find("jobs")
        if not all_jds:
            all_jds = [{
                "id": "job_default_backend",
                "title": "Software Development Engineer (Backend)",
                "company": "CareerPilot Benchmark",
                "domain": "Backend",
                "location": "Bengaluru / Remote",
                "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Git", "REST APIs", "System Design"],
                "description": "Design and build scalable backend services using Python, FastAPI, PostgreSQL, and Docker."
            }]
        if target_domain.lower() == "all":
            target_jds = all_jds
        else:
            filtered_jds = [j for j in all_jds if target_domain.lower() in j.get("domain", "").lower()]
            target_jds = filtered_jds if filtered_jds else all_jds

        # Ensure selected_job_id (e.g., custom or searched job) is included in matching
        selected_jd_obj: Optional[Dict[str, Any]] = None
        if selected_job_id:
            selected_jd_obj = next((j for j in all_jds if j.get("id") == selected_job_id), None)
            if selected_jd_obj and all(j.get("id") != selected_job_id for j in target_jds):
                target_jds = [selected_jd_obj] + target_jds

        # Step 5: Match resume to selected job and benchmark postings
        benchmark_results = []
        scores = []
        selected_job_match = None

        for jd in target_jds:
            eval_res = calculate_comprehensive_readiness(
                resume_text=parsed_resume["raw_text"],
                candidate_skills=verified_skills,
                jd=jd,
                leetcode_stats=leetcode_stats,
                github_stats=github_stats,
                projects=parsed_resume.get("projects", []),
                experience=parsed_resume.get("experience", [])
            )
            scores.append(eval_res["readiness_score"])
            match_entry = {
                "job_id": jd.get("id"),
                "title": jd.get("title"),
                "company": jd.get("company"),
                "domain": jd.get("domain", "Backend"),
                "location": jd.get("location"),
                "readiness_score": eval_res["readiness_score"],
                "matched_skills": eval_res["matched_skills"],
                "missing_skills": eval_res["missing_skills"],
                "unverified_skills": eval_res["unverified_skills"],
                "matching_evidence": eval_res["matching_evidence"],
                "next_steps": eval_res["next_steps"]
            }
            benchmark_results.append(match_entry)
            if selected_job_id and jd.get("id") == selected_job_id:
                selected_job_match = match_entry

        if not selected_job_match and benchmark_results:
            selected_job_match = benchmark_results[0]

        overall_readiness = (
            selected_job_match["readiness_score"]
            if (selected_job_id and selected_job_match)
            else (round(sum(scores) / len(scores), 1) if scores else 65.0)
        )

        # Construct Candidate Profile with Structured Information & Match Report
        profile_data = {
            "name": cand_name,
            "email": cand_email,
            "phone": cand_phone,
            "github_handle": gh_user,
            "github_stats": github_stats,
            "leetcode_handle": lc_user,
            "leetcode_stats": leetcode_stats,
            "linkedin_handle": li_user,
            "links": {
                "github_handle": gh_user,
                "leetcode_handle": lc_user,
                "linkedin_handle": li_user
            },
            "skills": verified_skills,
            "unverified_skills": candidate_unverified_skills,
            "skill_verification": skill_verification_map,
            "education": parsed_resume.get("education", []),
            "experience": parsed_resume.get("experience", []),
            "projects": parsed_resume.get("projects", []),
            "structured_by": parsed_resume.get("structured_by", "Continue without API"),
            "raw_resume_text": parsed_resume["raw_text"],
            "target_domain": target_domain,
            "overall_readiness_score": overall_readiness,
            "selected_job_match": selected_job_match,
            "benchmarks": benchmark_results
        }

        # Persist or update candidate in MongoDB / local DB
        await db.update_one(
            "profiles",
            {"email": profile_data["email"]},
            profile_data,
            upsert=True
        )

        print(f"[{self.name}] Completed assessment. Readiness Score: {overall_readiness}%")
        return profile_data

assessment_agent = AssessmentAgent()
