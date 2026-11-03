import math
import re
from typing import List, Dict, Any, Tuple

def tokenize_and_normalize(text: str) -> List[str]:
    """Tokenize and clean text into normalized n-grams and unigrams."""
    text = text.lower()
    tokens = re.findall(r"[a-z0-9+#]+", text)
    stopwords = {"and", "the", "with", "for", "in", "to", "of", "a", "an", "is", "we", "are", "you", "will", "our", "as", "on"}
    return [t for t in tokens if t not in stopwords and len(t) > 1]

def compute_tf(tokens: List[str]) -> Dict[str, float]:
    """Calculate term frequencies."""
    tf = {}
    for t in tokens:
        tf[t] = tf.get(t, 0.0) + 1.0
    total = len(tokens) or 1.0
    return {k: v / total for k, v in tf.items()}

def calculate_cosine_similarity(vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
    """Compute cosine similarity between two term-frequency sparse vectors."""
    all_keys = set(vec_a.keys()).union(set(vec_b.keys()))
    dot_product = sum(vec_a.get(k, 0.0) * vec_b.get(k, 0.0) for k in all_keys)
    
    norm_a = math.sqrt(sum(v ** 2 for v in vec_a.values()))
    norm_b = math.sqrt(sum(v ** 2 for v in vec_b.values()))
    
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot_product / (norm_a * norm_b)

def compute_skill_overlap(candidate_skills: List[str], required_skills: List[str]) -> Tuple[float, List[str], List[str]]:
    """Compute matched and missing skills with exact and substring normalization."""
    cand_lower = {s.lower().strip(): s for s in candidate_skills}
    matched = []
    missing = []

    for req in required_skills:
        req_low = req.lower().strip()
        found = False
        for c_low, orig_name in cand_lower.items():
            if req_low == c_low or req_low in c_low or c_low in req_low:
                matched.append(req)
                found = True
                break
        if not found:
            missing.append(req)

    match_ratio = len(matched) / (len(required_skills) or 1)
    return match_ratio, matched, missing


def analyze_skill_evidence(
    skill: str,
    projects: List[Dict[str, Any]],
    experience: List[Dict[str, Any]],
    github_stats: Dict[str, Any],
    leetcode_stats: Dict[str, Any]
) -> Tuple[bool, List[str]]:
    """
    Checks whether a claimed skill has concrete supporting evidence in the candidate's
    projects, experience, GitHub repositories, or LeetCode activity.
    """
    s_low = skill.lower().strip()
    sources = []

    # 1. Check Projects
    for proj in (projects or []):
        title = proj.get("title", "Project")
        bullets_text = " ".join(proj.get("bullets", [])) + " " + " ".join(proj.get("tech_stack", []))
        combined = f"{title} {bullets_text}".lower()
        if s_low in combined or any(s_low == t.lower() for t in proj.get("tech_stack", [])):
            sources.append(f"Project: {title}")

    # 2. Check Experience
    for exp in (experience or []):
        role = exp.get("role", "Experience")
        company = exp.get("company", "")
        exp_text = f"{role} {company} {' '.join(exp.get('highlights', []))}".lower()
        if s_low in exp_text:
            label = f"{role} ({company})" if company else role
            sources.append(f"Experience: {label}")

    # 3. Check GitHub verified languages
    gh_langs = [l.lower() for l in (github_stats or {}).get("top_languages", [])]
    if any(s_low == gl or s_low in gl for gl in gh_langs):
        sources.append(f"Verified on GitHub ({github_stats.get('public_repos', 0)} public repos)")

    # 4. Check LeetCode for DSA / Algorithmic skills
    if s_low in ("data structures", "algorithms", "data structures & algorithms", "dsa", "problem solving"):
        solved = (leetcode_stats or {}).get("total_solved", 0)
        if solved > 0:
            sources.append(f"Verified on LeetCode ({solved} problems solved)")

    return (len(sources) > 0, sources)


def calculate_comprehensive_readiness(
    resume_text: str,
    candidate_skills: List[str],
    jd: Dict[str, Any],
    leetcode_stats: Dict[str, Any] = None,
    github_stats: Dict[str, Any] = None,
    projects: List[Dict[str, Any]] = None,
    experience: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Step 5: Match resume to selected job.
    Identifies:
    - Matching evidence (project/experience/GitHub proof for each matched skill)
    - Missing or unverified skills (skills absent from resume vs claimed without project/GitHub proof)
    - Readiness score (weighted multi-signal score)
    - Next steps (actionable recommendations tailored to the job match)
    """
    req_skills = jd.get("required_skills", [])
    pref_skills = jd.get("preferred_skills", [])
    all_jd_skills = req_skills + pref_skills

    # 1. Skill Overlap
    skill_ratio, matched, missing = compute_skill_overlap(candidate_skills, req_skills)
    pref_ratio, pref_matched, pref_missing = compute_skill_overlap(candidate_skills, pref_skills)

    # 2. Evidence & Verification Audit across matched skills and candidate skills
    matching_evidence: List[Dict[str, Any]] = []
    unverified_skills: List[str] = []

    all_matched_jd_skills = matched + [p for p in pref_matched if p not in matched]
    for sk in all_matched_jd_skills:
        is_verified, evidence_list = analyze_skill_evidence(
            skill=sk,
            projects=projects or [],
            experience=experience or [],
            github_stats=github_stats or {},
            leetcode_stats=leetcode_stats or {}
        )
        if is_verified:
            matching_evidence.append({
                "skill": sk,
                "verified": True,
                "evidence": evidence_list[:2]
            })
        else:
            unverified_skills.append(sk)
            matching_evidence.append({
                "skill": sk,
                "verified": False,
                "evidence": ["Listed in Resume Skills section (no project/GitHub evidence found yet)"]
            })

    # 3. Semantic Similarity
    cand_vec = compute_tf(tokenize_and_normalize(resume_text + " " + " ".join(candidate_skills)))
    jd_vec = compute_tf(tokenize_and_normalize(jd.get("description", "") + " " + " ".join(all_jd_skills)))
    semantic_sim = calculate_cosine_similarity(cand_vec, jd_vec)

    # 4. LeetCode Signal (Normalized score: 150+ solved = 1.0)
    total_solved = (leetcode_stats or {}).get("total_solved", 0)
    leetcode_score = min(total_solved / 150.0, 1.0)

    # 5. GitHub Signal (Public repos + stars)
    repos_cnt = (github_stats or {}).get("public_repos", 0)
    stars_cnt = (github_stats or {}).get("total_stars", 0)
    github_score = min((repos_cnt * 0.1) + (stars_cnt * 0.05), 1.0)

    # Weighted aggregate score (0 to 100%)
    weighted_score = (
        (skill_ratio * 50.0) +
        (pref_ratio * 10.0) +
        (min(semantic_sim * 2.0, 1.0) * 20.0) +
        (leetcode_score * 12.0) +
        (github_score * 8.0)
    )

    final_percentage = round(min(max(weighted_score, 15.0), 96.0), 1)

    # 6. Actionable Next Steps for this Job Match
    next_steps: List[str] = []
    company_name = jd.get("company", "the employer")
    role_title = jd.get("title", "this role")

    if missing:
        top_missing = ", ".join(missing[:3])
        next_steps.append(f"Close skill gaps: Learn {top_missing} via the 14-Day Free Learning Plan (Step 2) to boost your match score for {company_name}.")
    if unverified_skills:
        top_unv = ", ".join(unverified_skills[:2])
        next_steps.append(f"Substantiate unverified skills ({top_unv}): Add measurable STAR project bullets demonstrating {top_unv} in Step 3 (Tailor Resume).")
    if final_percentage >= 70.0:
        next_steps.append(f"Strong readiness ({final_percentage}%): Generate your tailored STAR resume & cover letter for {role_title} at {company_name} in Step 3 and stage your application in Step 4.")
    else:
        next_steps.append(f"Tailor your existing projects to highlight {', '.join(matched[:3]) or 'core engineering fundamentals'} in Step 3 and practice role-specific technical questions in Step 5.")

    return {
        "readiness_score": final_percentage,
        "matched_skills": matched,
        "missing_skills": missing,
        "unverified_skills": unverified_skills,
        "preferred_matched": pref_matched,
        "preferred_missing": pref_missing,
        "matching_evidence": matching_evidence,
        "next_steps": next_steps,
        "semantic_similarity": round(semantic_sim, 2),
        "leetcode_signal": round(leetcode_score * 100, 1),
        "github_signal": round(github_score * 100, 1)
    }
