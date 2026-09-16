from typing import Dict, Any, List
from server.services.resume_parser import resume_parser
from server.services.github_service import github_service
from server.services.leetcode_service import leetcode_service

class AssessmentAgent:
    """Parses resume, queries public developer signals (GitHub, LeetCode), and builds a unified Skill Vector."""

    async def run(
        self,
        resume_text: str,
        github_username: str = "",
        leetcode_username: str = "",
        target_roles: List[str] = None
    ) -> Dict[str, Any]:
        target_roles = target_roles or ["Software Engineer", "Backend Developer"]
        
        # 1. Parse Resume
        parsed_resume = resume_parser.parse(resume_text)
        extracted_skills = parsed_resume["skills"]
        all_skills = list(parsed_resume["all_skills"])

        # 2. Fetch GitHub Signals
        github_data = await github_service.fetch_user_data(github_username)
        for lang in github_data.get("top_languages", []):
            if lang not in all_skills:
                all_skills.append(lang)
                if lang in extracted_skills.get("core_languages", []):
                    extracted_skills["core_languages"].append(lang)

        # 3. Fetch LeetCode Signals
        leetcode_data = await leetcode_service.fetch_user_data(leetcode_username)
        if leetcode_data.get("total_solved", 0) > 50:
            if "Data Structures" not in all_skills:
                all_skills.append("Data Structures")
            if "Algorithms" not in all_skills:
                all_skills.append("Algorithms")

        # 4. Calculate Overall Candidate Readiness Score (0-100)
        # Factors: Skill diversity (40%), LeetCode problem solving (30%), GitHub activity (20%), Profile completeness (10%)
        skill_score = min(40, len(all_skills) * 4)
        lc_score = min(30, int((leetcode_data.get("total_solved", 0) / 150) * 30))
        gh_score = min(20, (github_data.get("public_repos", 0) * 2) + min(10, github_data.get("stars_count", 0)))
        readiness_score = min(98, max(25, skill_score + lc_score + gh_score + 10))

        skill_vector = {
            "core_languages": extracted_skills.get("core_languages", []),
            "frameworks": extracted_skills.get("frameworks", []),
            "databases": extracted_skills.get("databases", []),
            "tools_devops": extracted_skills.get("tools_devops", []),
            "concepts": extracted_skills.get("concepts", []),
            "all_skills": sorted(list(set(all_skills))),
            "total_skills_count": len(set(all_skills)),
            "experience_level": "Fresher"
        }

        return {
            "parsed_name": parsed_resume.get("name", "Candidate"),
            "parsed_email": parsed_resume.get("email", ""),
            "parsed_phone": parsed_resume.get("phone", ""),
            "skill_vector": skill_vector,
            "github_data": github_data,
            "leetcode_data": leetcode_data,
            "readiness_score": readiness_score,
            "target_roles": target_roles
        }

assessment_agent = AssessmentAgent()

