import re
import html
import httpx
import asyncio
from typing import List, Dict, Any, Optional

def clean_html_text(raw_html: str) -> str:
    """Strip HTML tags and unescape entities for clean plain text descriptions."""
    if not raw_html:
        return ""
    clean = re.sub(r"<[^>]+>", " ", raw_html)
    clean = html.unescape(clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean

def infer_job_domain(title: str, tags: List[str], desc: str) -> str:
    """Infers the engineering domain for the job posting based on title and tags."""
    text = f"{title} {' '.join(tags)} {desc[:300]}".lower()
    
    if any(k in text for k in ["data", "machine learning", "ml", "ai", "deep learning", "nlp", "analytics"]):
        return "Data / AI"
    if any(k in text for k in ["devops", "cloud", "infrastructure", "kubernetes", "docker", "sre", "aws", "azure"]):
        return "DevOps / Cloud"
    if any(k in text for k in ["frontend", "front-end", "ui", "react", "vue", "angular", "css", "web design"]):
        return "Frontend"
    if any(k in text for k in ["full stack", "fullstack", "full-stack"]):
        return "Full Stack"
    if any(k in text for k in ["backend", "back-end", "python", "java", "golang", "go", "node", "api", "database", "sql"]):
        return "Backend"
    return "Full Stack"

async def fetch_remotive_jobs(limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch live software engineering jobs from Remotive's free public API."""
    url = f"https://remotive.com/api/remote-jobs?category=software-dev&limit={limit}"
    async with httpx.AsyncClient(timeout=8.0) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()
        jobs_raw = data.get("jobs", [])
        
        parsed_jobs = []
        for idx, item in enumerate(jobs_raw[:limit]):
            title = item.get("title", "Software Engineer")
            company = item.get("company_name", "Tech Company")
            tags = item.get("tags", [])
            desc_clean = clean_html_text(item.get("description", ""))
            domain = infer_job_domain(title, tags, desc_clean)
            
            # Format skills
            skills = [t.capitalize() for t in tags if len(t) > 1]
            if not skills:
                skills = ["Git", "REST APIs", "Problem Solving"]
            
            job_id = f"live-remotive-{item.get('id', idx)}"
            portal_url = item.get("url", "https://remotive.com")
            encoded_query = f"{company} {title}".replace(" ", "+")
            
            parsed_jobs.append({
                "id": job_id,
                "title": title,
                "company": company,
                "location": item.get("candidate_required_location") or "Remote / Global",
                "domain": domain,
                "experience": "0-3 Years",
                "salary": item.get("salary") or "Competitive Tech Salary",
                "description": desc_clean[:500] + "..." if len(desc_clean) > 500 else desc_clean,
                "required_skills": skills[:6],
                "preferred_skills": skills[6:10] if len(skills) > 6 else ["Docker", "CI/CD", "Testing"],
                "portal_url": portal_url,
                "apply_search_url": f"https://www.linkedin.com/jobs/search/?keywords={encoded_query}",
                "is_live": True,
                "source": "Remotive API"
            })
        return parsed_jobs

async def fetch_arbeitnow_jobs(limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch live software engineering jobs from Arbeitnow's free public API."""
    url = "https://www.arbeitnow.com/api/job-board-api"
    async with httpx.AsyncClient(timeout=8.0) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()
        items = data.get("data", [])
        
        parsed_jobs = []
        for idx, item in enumerate(items[:limit]):
            title = item.get("title", "Developer")
            company = item.get("company_name", "Tech Corp")
            tags = item.get("tags", [])
            desc_clean = clean_html_text(item.get("description", ""))
            domain = infer_job_domain(title, tags, desc_clean)
            
            skills = [t.strip().capitalize() for t in tags if t.strip()]
            if not skills:
                skills = ["Git", "REST APIs", "Python", "SQL"]
                
            job_id = f"live-arbeit-{item.get('slug', idx)[:20]}"
            portal_url = item.get("url", "https://www.arbeitnow.com")
            encoded_query = f"{company} {title}".replace(" ", "+")
            
            parsed_jobs.append({
                "id": job_id,
                "title": title,
                "company": company,
                "location": item.get("location") or "Remote",
                "domain": domain,
                "experience": "0-2 Years",
                "salary": "Market Rate (LPA/EUR)",
                "description": desc_clean[:500] + "..." if len(desc_clean) > 500 else desc_clean,
                "required_skills": skills[:6],
                "preferred_skills": skills[6:10] if len(skills) > 6 else ["Agile", "Docker", "Unit Testing"],
                "portal_url": portal_url,
                "apply_search_url": f"https://www.linkedin.com/jobs/search/?keywords={encoded_query}",
                "is_live": True,
                "source": "Arbeitnow API"
            })
        return parsed_jobs

async def fetch_all_live_jobs(limit_per_source: int = 6) -> List[Dict[str, Any]]:
    """
    Attempts to fetch live jobs from public APIs.
    Tries Remotive first, falls back to Arbeitnow, and combines results.
    """
    results = []
    try:
        remotive_jobs = await fetch_remotive_jobs(limit=limit_per_source)
        if remotive_jobs:
            results.extend(remotive_jobs)
    except Exception as e:
        print(f"[JobFetcher] Remotive API fetch warning: {e}")

    try:
        arbeit_jobs = await fetch_arbeitnow_jobs(limit=limit_per_source)
        if arbeit_jobs:
            results.extend(arbeit_jobs)
    except Exception as e:
        print(f"[JobFetcher] Arbeitnow API fetch warning: {e}")

    return results
