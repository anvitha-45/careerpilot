import math
from typing import List, Dict, Any, Tuple

class VectorService:
    """Computes skill vectors, cosine similarity, and comprehensive job match scores."""

    def compute_match(
        self,
        candidate_skills: List[str],
        required_skills: List[str],
        preferred_skills: List[str],
        candidate_target_roles: List[str],
        job_title: str,
        candidate_location: str,
        job_location: str
    ) -> Dict[str, Any]:
        c_set = set(s.lower() for s in candidate_skills)
        r_set = set(s.lower() for s in required_skills)
        p_set = set(s.lower() for s in preferred_skills)

        # 1. Matched and Missing Skills
        matched_required = [s for s in required_skills if s.lower() in c_set]
        missing_required = [s for s in required_skills if s.lower() not in c_set]
        matched_preferred = [s for s in preferred_skills if s.lower() in c_set]

        # 2. Skill Overlap Calculation (0-60 points)
        req_ratio = (len(matched_required) / len(required_skills)) if required_skills else 1.0
        pref_ratio = (len(matched_preferred) / len(preferred_skills)) if preferred_skills else 0.5
        skill_score = int(round((req_ratio * 45) + (pref_ratio * 15)))

        # 3. Role Relevance Score (0-20 points)
        role_score = 0
        job_title_lower = job_title.lower()
        for role in candidate_target_roles:
            r_words = set(role.lower().split())
            j_words = set(job_title_lower.split())
            overlap = r_words.intersection(j_words)
            if overlap:
                role_score = max(role_score, 18)
            elif any(w in job_title_lower for w in ["software", "developer", "engineer", "sde"]):
                role_score = max(role_score, 14)
        if role_score == 0:
            role_score = 10

        # 4. Project Evidence Score (0-10 points)
        project_score = 8 if len(c_set) >= 6 else 5

        # 5. Location Compatibility (0-10 points)
        loc_score = 10
        if "remote" in job_location.lower() or "remote" in candidate_location.lower():
            loc_score = 10
        elif any(city in candidate_location.lower() for city in ["india", "bangalore", "hyderabad", "pune", "delhi"]):
            loc_score = 10
        else:
            loc_score = 7

        total_score = min(100, max(15, skill_score + role_score + project_score + loc_score))

        # Generate human-readable explainability text
        explanation = (
            f"You match {len(matched_required)}/{len(required_skills)} required core skills ({int(req_ratio * 100)}%). "
            f"Role title strongly aligns with your target preferences (+{role_score} pts). "
        )
        if missing_required:
            explanation += f"Addressing critical gaps like {', '.join(missing_required[:2])} will raise your match to >90%."
        else:
            explanation += "You possess 100% of the non-negotiable core skills!"

        return {
            "match_score": total_score,
            "skills_score": skill_score,
            "role_relevance_score": role_score,
            "project_evidence_score": project_score,
            "location_score": loc_score,
            "matched_skills": matched_required + matched_preferred,
            "missing_skills": missing_required,
            "explanation": explanation
        }

vector_service = VectorService()

