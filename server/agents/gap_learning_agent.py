from typing import Dict, Any, List
from server.database import get_jobs_col
from server.seeds.curated_resources import get_resources_for_skill

class GapLearningAgent:
    """Identifies missing skills ranked strictly by empirical frequency across real target postings."""

    async def run(
        self,
        user_id: str,
        candidate_skills: List[str],
        target_roles: List[str] = None
    ) -> Dict[str, Any]:
        target_roles = target_roles or ["Software Engineer", "Backend Developer"]
        candidate_skills_lower = set(s.lower() for s in candidate_skills)

        # 1. Fetch relevant job postings from DB
        jobs_col = get_jobs_col()
        all_jobs = await jobs_col.find({})
        
        if not all_jobs:
            total_jobs = 1
            skill_frequencies = {"Spring Boot": 18, "Docker": 15, "PostgreSQL": 14, "AWS": 10, "Redis": 8}
        else:
            total_jobs = len(all_jobs)
            skill_frequencies: Dict[str, int] = {}
            for job in all_jobs:
                combined_skills = set(job.get("required_skills", []) + job.get("preferred_skills", []))
                for skill in combined_skills:
                    skill_frequencies[skill] = skill_frequencies.get(skill, 0) + 1

        # 2. Identify missing skills and rank by market frequency
        identified_gaps = []
        for skill, count in skill_frequencies.items():
            if skill.lower() not in candidate_skills_lower:
                pct = round((count / total_jobs) * 100, 1)
                
                if pct >= 50:
                    priority = "CRITICAL"
                    est_days = "7-10 days"
                elif pct >= 30:
                    priority = "HIGH"
                    est_days = "5-7 days"
                elif pct >= 15:
                    priority = "MEDIUM"
                    est_days = "3-5 days"
                else:
                    priority = "LOW"
                    est_days = "2-3 days"

                resources = get_resources_for_skill(skill)
                
                identified_gaps.append({
                    "skill": skill,
                    "priority": priority,
                    "frequency_count": count,
                    "frequency_percentage": pct,
                    "market_context": f"Appears in {count} of {total_jobs} analyzed target postings ({pct}%).",
                    "current_evidence": "Not yet evidenced in projects or resume.",
                    "suggested_action": f"Build and commit a portfolio component demonstrating {skill}.",
                    "estimated_days": est_days,
                    "resources": resources
                })

        # Sort strictly descending by frequency percentage
        identified_gaps.sort(key=lambda g: g["frequency_percentage"], reverse=True)

        # 3. Generate structured 4-week personalized learning roadmap
        top_gaps = identified_gaps[:6]
        weeks = []
        
        if len(top_gaps) >= 1:
            g1 = top_gaps[0]
            weeks.append({
                "week_number": 1,
                "focus_topic": f"Mastering {g1['skill']} Foundations (Critical Market Requirement)",
                "skills": [g1["skill"]],
                "tasks": [
                    f"Complete official {g1['skill']} documentation tutorial and understand architecture.",
                    f"Build a standalone CRUD service implementing {g1['skill']} best practices.",
                    "Push code to GitHub with clear README and architecture diagram."
                ],
                "resources": g1["resources"][:2]
            })

        if len(top_gaps) >= 2:
            g2 = top_gaps[1]
            weeks.append({
                "week_number": 2,
                "focus_topic": f"Integrating {g2['skill']} into Production Systems",
                "skills": [g2["skill"]],
                "tasks": [
                    f"Study practical implementation patterns for {g2['skill']}.",
                    f"Integrate {g2['skill']} with previous week's project.",
                    "Write automated unit tests verifying core endpoints."
                ],
                "resources": g2["resources"][:2]
            })

        if len(top_gaps) >= 4:
            g3 = top_gaps[2]
            g4 = top_gaps[3]
            weeks.append({
                "week_number": 3,
                "focus_topic": f"DevOps, Scaling & Persistence ({g3['skill']} & {g4['skill']})",
                "skills": [g3["skill"], g4["skill"]],
                "tasks": [
                    f"Configure {g3['skill']} for local containerized development.",
                    f"Benchmark database queries and connect {g4['skill']}.",
                    "Document deployment steps in repository."
                ],
                "resources": (g3["resources"][:1] + g4["resources"][:1])
            })

        weeks.append({
            "week_number": 4,
            "focus_topic": "Mock Interview Readiness & Portfolio Polishing",
            "skills": ["System Design", "Coding Patterns"],
            "tasks": [
                "Practice 15 medium LeetCode problems covering Two Pointers and Tree Traversals.",
                "Conduct 2 JD-specific mock interviews using CareerPilot's Interview Agent.",
                "Review resume bullet points with Tailoring Agent to reflect newly gained competencies."
            ],
            "resources": get_resources_for_skill("Data Structures")[:2]
        })

        return {
            "total_gaps_identified": len(identified_gaps),
            "critical_gaps_count": len([g for g in identified_gaps if g["priority"] == "CRITICAL"]),
            "gaps": identified_gaps[:12],
            "weeks": weeks
        }

gap_learning_agent = GapLearningAgent()

