import asyncio
from typing import Dict, Any, List
from server.utils.resume_parser import parse_full_resume
from server.utils.github_client import fetch_github_profile
from server.utils.leetcode_client import fetch_leetcode_profile
from server.utils.similarity import calculate_comprehensive_readiness
from server.database import db

class AssessmentAgent:
    """Agent 1: Ingests resume, validates public profiles (GitHub/LeetCode), and benchmarks against real JDs."""

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
        target_domain: str = "Backend"
    ) -> Dict[str, Any]:
        print(f"[{self.name}] Initiating multi-source candidate assessment...")

        # 1. Parse Resume Content
        parsed_resume = parse_full_resume(resume_bytes_or_text)
        
        # Override handles & contact info if candidate provided in input form
        cand_name = full_name.strip() or parsed_resume.get("name") or "Candidate"
        cand_email = email.strip() or parsed_resume.get("email") or "candidate@example.com"
        cand_phone = phone.strip() or parsed_resume.get("phone") or "+91 9876543210"
        gh_user = github_handle.strip() or parsed_resume.get("github_handle", "")
        lc_user = leetcode_handle.strip() or parsed_resume.get("leetcode_handle", "")
        li_user = parsed_resume.get("linkedin_handle", "")

        # 2. Concurrently fetch verified signals from GitHub and LeetCode
        gh_task = fetch_github_profile(gh_user) if gh_user else asyncio.sleep(0, result={})
        lc_task = fetch_leetcode_profile(lc_user) if lc_user else asyncio.sleep(0, result={})
        github_stats, leetcode_stats = await asyncio.gather(gh_task, lc_task)

        # Merge extracted resume skills with languages verified in GitHub
        all_skills = set(parsed_resume["skills"])
        if github_stats.get("top_languages"):
            for lang in github_stats["top_languages"]:
                all_skills.add(lang)
        verified_skills = sorted(list(all_skills))

        # 3. Retrieve target JDs from database
        all_jds = await db.find("jobs")
        # Filter by domain if not "All", else take all JDs
        if target_domain.lower() == "all":
            target_jds = all_jds
        else:
            filtered_jds = [j for j in all_jds if target_domain.lower() in j.get("domain", "").lower()]
            target_jds = filtered_jds if filtered_jds else all_jds

        # 4. Benchmark against target JDs
        benchmark_results = []
        scores = []
        for jd in target_jds:
            eval_res = calculate_comprehensive_readiness(
                resume_text=parsed_resume["raw_text"],
                candidate_skills=verified_skills,
                jd=jd,
                leetcode_stats=leetcode_stats,
                github_stats=github_stats
            )
            scores.append(eval_res["readiness_score"])
            benchmark_results.append({
                "job_id": jd.get("id"),
                "title": jd.get("title"),
                "company": jd.get("company"),
                "location": jd.get("location"),
                "is_custom": jd.get("is_custom", False),
                "readiness_score": eval_res["readiness_score"],
                "matched_skills": eval_res["matched_skills"],
                "missing_skills": eval_res["missing_skills"]
            })

        overall_readiness = round(sum(scores) / len(scores), 1) if scores else 65.0

        # Construct Candidate Profile
        profile_data = {
            "name": cand_name,
            "email": cand_email,
            "phone": cand_phone,
            "github_handle": gh_user,
            "github_stats": github_stats,
            "leetcode_handle": lc_user,
            "leetcode_stats": leetcode_stats,
            "linkedin_handle": li_user,
            "skills": verified_skills,
            "raw_resume_text": parsed_resume["raw_text"],
            "projects": parsed_resume["projects"],
            "target_domain": target_domain,
            "overall_readiness_score": overall_readiness,
            "benchmarks": benchmark_results
        }

        # Persist or update candidate in MongoDB
        await db.update_one(
            "profiles",
            {"email": profile_data["email"]},
            profile_data,
            upsert=True
        )

        print(f"[{self.name}] Completed assessment. Readiness Score: {overall_readiness}%")
        return profile_data

assessment_agent = AssessmentAgent()

