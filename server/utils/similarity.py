import math
import re
from typing import List, Dict, Any, Tuple

def tokenize_and_normalize(text: str) -> List[str]:
    """Tokenize and clean text into normalized n-grams and unigrams."""
    text = text.lower()
    # Replace special chars with spaces
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
        # Direct match or substring containment (e.g. 'Postgres' in 'PostgreSQL')
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

def calculate_comprehensive_readiness(
    resume_text: str,
    candidate_skills: List[str],
    jd: Dict[str, Any],
    leetcode_stats: Dict[str, Any] = None,
    github_stats: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Weighted Readiness Metric:
    - 50% Required Technical Skills Coverage
    - 25% Resume Semantic Context Matching (TF-IDF Cosine Similarity)
    - 15% Verified LeetCode Problem Solving Signal
    - 10% GitHub Public Development Signal
    """
    req_skills = jd.get("required_skills", [])
    pref_skills = jd.get("preferred_skills", [])
    all_jd_skills = req_skills + pref_skills

    # 1. Skill Overlap
    skill_ratio, matched, missing = compute_skill_overlap(candidate_skills, req_skills)
    pref_ratio, pref_matched, _ = compute_skill_overlap(candidate_skills, pref_skills)

    # 2. Semantic Similarity
    cand_vec = compute_tf(tokenize_and_normalize(resume_text + " " + " ".join(candidate_skills)))
    jd_vec = compute_tf(tokenize_and_normalize(jd.get("description", "") + " " + " ".join(all_jd_skills)))
    semantic_sim = calculate_cosine_similarity(cand_vec, jd_vec)

    # 3. LeetCode Signal (Normalized score: 100+ solved = 1.0)
    total_solved = (leetcode_stats or {}).get("total_solved", 0)
    leetcode_score = min(total_solved / 150.0, 1.0)

    # 4. GitHub Signal (Public repos + stars)
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

    return {
        "readiness_score": final_percentage,
        "matched_skills": matched,
        "missing_skills": missing,
        "preferred_matched": pref_matched,
        "semantic_similarity": round(semantic_sim, 2),
        "leetcode_signal": round(leetcode_score * 100, 1),
        "github_signal": round(github_score * 100, 1)
    }
