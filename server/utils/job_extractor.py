import re
import uuid
import json
import urllib.parse
from html.parser import HTMLParser
from typing import Dict, Any, List, Optional
import httpx
from server.config import settings

class HTMLTextExtractor(HTMLParser):
    """Clean HTML text extractor that removes scripts, styles, and tags."""
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []
        self.ignore = False
        self.title = ""
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        if tag.lower() in ("script", "style", "noscript", "svg", "header", "footer", "nav"):
            self.ignore = True
        elif tag.lower() == "title":
            self.in_title = True

    def handle_endtag(self, tag):
        if tag.lower() in ("script", "style", "noscript", "svg", "header", "footer", "nav"):
            self.ignore = False
        elif tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        elif not self.ignore:
            self.fed.append(data)

    def get_text(self) -> str:
        raw = " ".join(self.fed)
        return re.sub(r"\s+", " ", raw).strip()

TECH_SKILLS_DICTIONARY = [
    # Languages
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust", "PHP", "Ruby", "Kotlin", "Swift", "Scala", "SQL", "Bash",
    # Frameworks & Libraries
    "FastAPI", "Flask", "Django", "Spring Boot", "React", "Next.js", "Angular", "Vue", "Node.js", "Express", "ASP.NET",
    "PyTorch", "TensorFlow", "Pandas", "NumPy", "Scikit-Learn", "HTML5", "CSS3", "Tailwind CSS",
    # Databases & Caches
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "Cassandra", "DynamoDB", "SQLite", "Elasticsearch",
    # Cloud, DevOps & Tools
    "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Terraform", "CI/CD", "Git", "GitHub", "Linux",
    "Kafka", "RabbitMQ", "Microservices", "REST APIs", "GraphQL", "Postman", "Celery", "Airflow"
]

def clean_html_to_text(html_content: str) -> Dict[str, str]:
    """Parse HTML content to plain text and page title."""
    try:
        parser = HTMLTextExtractor()
        parser.feed(html_content)
        return {
            "title": parser.title.strip(),
            "text": parser.get_text()[:6000]
        }
    except Exception:
        # Fallback regex extraction
        title_match = re.search(r"<title[^>]*>(.*?)</title>", html_content, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else ""
        text = re.sub(r"<[^>]+>", " ", html_content)
        text = re.sub(r"\s+", " ", text).strip()
        return {"title": title, "text": text[:6000]}

def extract_company_from_url(url: str) -> str:
    """Extract clean company name from domain or path."""
    try:
        parsed = urllib.parse.urlparse(url)
        netloc = parsed.netloc.lower()
        # Remove subdomains like www, jobs, careers, boards
        parts = netloc.split(".")
        if len(parts) >= 2:
            domain_name = parts[-2]
            if domain_name in ("greenhouse", "lever", "smartrecruiters", "workday", "linkedin", "indeed", "naukri"):
                # Check path for company slug (e.g. boards.greenhouse.io/stripe/jobs)
                path_parts = [p for p in parsed.path.split("/") if p]
                if path_parts:
                    return path_parts[0].capitalize()
            return domain_name.capitalize()
    except Exception:
        pass
    return "Tech Company"

async def fetch_job_page(url: str) -> Dict[str, Any]:
    """Asynchronously fetch webpage text with standard browser headers."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    async with httpx.AsyncClient(timeout=12.0, follow_redirects=True, headers=headers) as client:
        resp = await client.get(url)
        if resp.status_code == 200:
            extracted = clean_html_to_text(resp.text)
            return {
                "success": True,
                "title": extracted["title"],
                "text": extracted["text"],
                "url": str(resp.url)
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {resp.status_code}: Unable to access job page directly.",
                "title": "",
                "text": "",
                "url": url
            }

async def call_llm_for_job_extraction(content: str, source_url: str = "") -> Optional[Dict[str, Any]]:
    """Use Gemini or Groq to parse job text into structured JSON."""
    system_prompt = (
        "You are an expert Technical Recruiter and Job Parser. "
        "Extract structured JSON describing the job posting from the provided text. "
        "Strictly return ONLY valid JSON with keys: "
        "'title' (string), 'company' (string), 'domain' ('Backend', 'Frontend', 'Full Stack', 'DevOps / Cloud', or 'Data / AI'), "
        "'location' (string), 'experience' (string), 'salary' (string), 'description' (string, 2-3 sentences), "
        "'required_skills' (list of strings), 'preferred_skills' (list of strings)."
    )

    prompt = f"Source URL: {source_url}\n\nJob Posting Content:\n{content[:4000]}"

    # 1. Try Gemini Flash
    if settings.GEMINI_API_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
            payload = {
                "contents": [{"parts": [{"text": f"{system_prompt}\n\n{prompt}"}]}],
                "generationConfig": {"temperature": 0.2, "maxOutputTokens": 800}
            }
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    candidates = resp.json().get("candidates", [])
                    if candidates:
                        raw_ans = candidates[0]["content"]["parts"][0]["text"].strip()
                        clean_json = raw_ans.replace("```json", "").replace("```", "").strip()
                        return json.loads(clean_json)
        except Exception as e:
            print(f"[JobExtractor] Gemini extraction failed: {e}")

    # 2. Try Groq
    if settings.GROQ_API_KEY:
        try:
            headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": "llama-3.1-70b-versatile",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2
            }
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
                if resp.status_code == 200:
                    raw_ans = resp.json()["choices"][0]["message"]["content"].strip()
                    clean_json = raw_ans.replace("```json", "").replace("```", "").strip()
                    return json.loads(clean_json)
        except Exception as e:
            print(f"[JobExtractor] Groq extraction failed: {e}")

    return None

def heuristic_extract_job(content: str, html_title: str = "", source_url: str = "") -> Dict[str, Any]:
    """Deterministic heuristic job parser when LLMs are offline or unavailable."""
    company = extract_company_from_url(source_url) if source_url else "Tech Corp"
    
    # Infer title from html_title or first lines
    title = "Software Engineer"
    candidate_title = html_title or ""
    if candidate_title:
        # e.g., "Full Stack Developer at Razorpay" -> "Full Stack Developer"
        clean_title = re.split(r"[-|–—:]|\bat\b", candidate_title, flags=re.IGNORECASE)[0].strip()
        if len(clean_title) > 3 and len(clean_title) < 60:
            title = clean_title
    else:
        # Search for title in first 500 chars
        title_matches = re.findall(r"(?:Junior|Senior|Associate|Lead)?\s*(?:Software|Backend|Frontend|Full Stack|DevOps|Data|Machine Learning|Cloud|AI)\s*(?:Engineer|Developer|Specialist|Trainee)", content[:500], re.IGNORECASE)
        if title_matches:
            title = title_matches[0].strip()

    # Extract detected technical skills
    content_lower = content.lower()
    found_skills = []
    for skill in TECH_SKILLS_DICTIONARY:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, content_lower):
            found_skills.append(skill)

    if not found_skills:
        found_skills = ["Python", "FastAPI", "SQL", "Git", "REST APIs"]

    req_skills = found_skills[:7]
    pref_skills = found_skills[7:12] if len(found_skills) > 7 else ["Docker", "Linux", "Microservices"]

    # Infer domain
    domain = "Backend"
    skills_set = {s.lower() for s in found_skills}
    if {"react", "angular", "vue", "html5", "css3", "tailwind css"}.intersection(skills_set) and not {"fastapi", "spring boot", "django"}.intersection(skills_set):
        domain = "Frontend"
    elif ({"react", "vue", "angular"}.intersection(skills_set) and {"node.js", "python", "fastapi", "django", "express"}.intersection(skills_set)) or "full stack" in title.lower():
        domain = "Full Stack"
    elif {"docker", "kubernetes", "aws", "terraform", "ci/cd"}.intersection(skills_set) or "devops" in title.lower():
        domain = "DevOps / Cloud"
    elif {"pytorch", "tensorflow", "pandas", "scikit-learn", "numpy"}.intersection(skills_set) or "data" in title.lower() or "ml" in title.lower():
        domain = "Data / AI"

    # Location heuristic
    location = "Bengaluru, India (Hybrid)"
    if "remote" in content_lower:
        location = "Remote / Flexible"
    elif "hyderabad" in content_lower:
        location = "Hyderabad, India"
    elif "mumbai" in content_lower or "pune" in content_lower:
        location = "Pune / Mumbai, India"

    # Experience heuristic
    experience = "0-2 Years"
    exp_match = re.search(r"(\d+[\s–-]+\d+)\s*(?:years?|yrs)", content_lower)
    if exp_match:
        experience = f"{exp_match.group(1)} Years"

    desc = content[:250].strip() + "..." if len(content) > 100 else f"Opportunity for {title} at {company} working on modern software development."

    return {
        "title": title,
        "company": company,
        "domain": domain,
        "location": location,
        "experience": experience,
        "salary": "₹8 - ₹14 LPA (Estimated)",
        "description": desc,
        "required_skills": req_skills,
        "preferred_skills": pref_skills
    }

async def process_job_input(url: str = "", raw_text: str = "") -> Dict[str, Any]:
    """
    Main ingestion function:
    1. Fetches webpage text if URL provided.
    2. Fallbacks to provided raw_text if fetch is blocked or failed.
    3. Runs LLM extraction, falling back to heuristics.
    4. Returns fully structured Job dictionary ready for insertion & benchmarking.
    """
    content = ""
    html_title = ""
    effective_url = (url or "").strip()

    if effective_url:
        if not effective_url.startswith("http://") and not effective_url.startswith("https://"):
            effective_url = "https://" + effective_url
        page_res = await fetch_job_page(effective_url)
        if page_res.get("success"):
            content = page_res.get("text", "")
            html_title = page_res.get("title", "")
        else:
            # If fetch failed (e.g. login wall / Cloudflare) but raw text was provided, use raw text
            if raw_text and raw_text.strip():
                content = raw_text.strip()
            else:
                # Still try to extract company and make a functional entry based on URL
                content = f"Job listing from {effective_url}. Role and requirements at {extract_company_from_url(effective_url)}."

    elif raw_text and raw_text.strip():
        content = raw_text.strip()

    if not content:
        raise ValueError("Please provide either a valid Job Posting URL or paste the job description text.")

    # Try LLM first
    structured = await call_llm_for_job_extraction(content, effective_url)
    if not structured or not structured.get("title") or not structured.get("company"):
        structured = heuristic_extract_job(content, html_title, effective_url)

    # Clean up fields
    job_id = f"custom-{uuid.uuid4().hex[:8]}"
    company = structured.get("company", "Target Company").strip()
    title = structured.get("title", "Software Engineer").strip()

    search_query = urllib.parse.quote_plus(f"{company} {title}")
    apply_search = f"https://www.linkedin.com/jobs/search/?keywords={search_query}"

    return {
        "id": job_id,
        "title": title,
        "company": company,
        "location": structured.get("location", "Bengaluru, India (Hybrid)"),
        "domain": structured.get("domain", "Backend"),
        "experience": structured.get("experience", "0-2 Years"),
        "salary": structured.get("salary", "Competitive"),
        "description": structured.get("description", f"Hiring for {title} at {company}."),
        "required_skills": structured.get("required_skills", ["Python", "FastAPI", "PostgreSQL", "Git"]),
        "preferred_skills": structured.get("preferred_skills", ["Docker", "Redis", "AWS"]),
        "portal_url": effective_url or apply_search,
        "apply_search_url": apply_search,
        "is_custom": True
    }
