import os
import json
from typing import Dict, Any, List
from server.database import db
from server.utils.ai_config import call_llm

class GapLearningAgent:
    """Agent 2: Identifies missing skills ranked by frequency in real job postings and maps to free resources."""

    def __init__(self):
        self.name = "Gap & Learning Agent"
        self.resources_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "curated_resources.json")
        self.curated_resources = self._load_curated_resources()

    def _load_curated_resources(self) -> Dict[str, Any]:
        try:
            if os.path.exists(self.resources_path):
                with open(self.resources_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"[{self.name}] Error loading curated resources: {e}")
        return {}

    async def execute(self, candidate_profile: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[{self.name}] Analyzing market demand gaps for candidate: {candidate_profile.get('name')}...")
        candidate_skills = [s.lower().strip() for s in candidate_profile.get("skills", [])]
        target_domain = candidate_profile.get("target_domain", "Backend")

        # 1. Fetch all JDs relevant to domain
        all_jds = await db.find("jobs")
        if target_domain.lower() == "all":
            active_jds = all_jds
        else:
            domain_jds = [j for j in all_jds if target_domain.lower() in j.get("domain", "").lower()]
            active_jds = domain_jds if domain_jds else all_jds
        total_jds = len(active_jds) or 1

        # 2. Count empirical skill frequency across target postings
        skill_counts: Dict[str, int] = {}
        for jd in active_jds:
            reqs = jd.get("required_skills", []) + jd.get("preferred_skills", [])
            for s in reqs:
                s_clean = s.strip()
                skill_counts[s_clean] = skill_counts.get(s_clean, 0) + 1

        # 3. Detect candidate gaps & calculate market prevalence percentage
        ranked_gaps = []
        for skill_name, count in sorted(skill_counts.items(), key=lambda x: x[1], reverse=True):
            skill_low = skill_name.lower()
            # If not in candidate skills
            if not any(skill_low == cs or skill_low in cs or cs in skill_low for cs in candidate_skills):
                prevalence_pct = round((count / total_jds) * 100, 1)
                # Lookup resources
                resources = self.curated_resources.get(skill_name, [
                    {
                        "platform": "Official Docs",
                        "title": f"Learn {skill_name} Official Guide & Documentation",
                        "instructor": f"{skill_name} Core Team",
                        "url": f"https://www.google.com/search?q={skill_name}+official+documentation",
                        "type": "Documentation",
                        "duration": "Self-paced"
                    },
                    {
                        "platform": "YouTube",
                        "title": f"{skill_name} Crash Course for Developers",
                        "instructor": "freeCodeCamp / Traversy Media",
                        "url": f"https://www.youtube.com/results?search_query={skill_name}+full+course",
                        "type": "Video",
                        "duration": "3 Hours"
                    }
                ])

                ranked_gaps.append({
                    "skill": skill_name,
                    "postings_count": count,
                    "market_demand_percentage": prevalence_pct,
                    "priority": "Critical" if prevalence_pct >= 60 else ("High" if prevalence_pct >= 40 else "Recommended"),
                    "resources": resources
                })

        # 4. Construct a structured 14-Day Micro-Learning Roadmap
        roadmap_days = []
        top_skills = ranked_gaps[:4]
        llm_outcomes: Dict[str, str] = {}
        if top_skills:
            skills_list_str = ", ".join(g["skill"] for g in top_skills)
            llm_resp = await call_llm(
                prompt=(
                    f"Target Domain: {target_domain}\n"
                    f"Candidate Existing Skills: {', '.join(candidate_profile.get('skills', [])[:8])}\n"
                    f"Missing High-Demand Skills: {skills_list_str}\n\n"
                    f"Return a JSON object mapping each missing skill name to a concise 1-sentence practical micro-project goal "
                    f"(under 18 words) that a student can build in 3 days. Return ONLY valid JSON."
                ),
                system_prompt="You are an engineering mentor creating practical 3-day micro-project goals for graduating software engineers.",
                temperature=0.3,
                max_tokens=300,
                caller_name=self.name
            )
            if llm_resp:
                try:
                    clean_json = llm_resp.strip().replace("```json", "").replace("```", "").strip()
                    parsed_outcomes = json.loads(clean_json)
                    if isinstance(parsed_outcomes, dict):
                        llm_outcomes = parsed_outcomes
                except Exception:
                    pass

        for i, gap in enumerate(top_skills):
            day_start = (i * 3) + 1
            day_end = (i * 3) + 3
            sk_name = gap["skill"]
            custom_outcome = llm_outcomes.get(sk_name) or f"Build a practical micro-project demonstrating {sk_name} integration"
            roadmap_days.append({
                "period": f"Days {day_start}–{day_end}",
                "focus_skill": sk_name,
                "target_outcome": custom_outcome,
                "recommended_resource": gap["resources"][0] if gap["resources"] else None
            })

        result = {
            "total_postings_analyzed": total_jds,
            "ranked_gaps": ranked_gaps,
            "top_missing_skills": [g["skill"] for g in ranked_gaps[:5]],
            "fourteen_day_roadmap": roadmap_days
        }

        # Persist to database
        await db.update_one(
            "learning",
            {"email": candidate_profile.get("email")},
            {"email": candidate_profile.get("email"), **result},
            upsert=True
        )

        print(f"[{self.name}] Completed gap analysis. Found {len(ranked_gaps)} ranked gaps.")
        return result

gap_learning_agent = GapLearningAgent()

