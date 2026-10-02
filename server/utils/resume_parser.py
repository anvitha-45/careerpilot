import re
import io
from typing import Dict, List, Any

# Canonical Skill Taxonomy for Graduating Engineers
TECH_SKILL_PATTERNS = {
    "Languages": [
        "python", "javascript", "typescript", "java", "c\\+\\+", "c#", "c", "golang", "go",
        "ruby", "rust", "php", "swift", "kotlin", "scala", "sql", "bash", "html5?", "css3?"
    ],
    "Frameworks & Libraries": [
        "react(\\.?js)?", "next(\\.?js)?", "vue(\\.?js)?", "angular", "node(\\.?js)?",
        "express(\\.?js)?", "fastapi", "flask", "django", "spring boot", "spring",
        "dotnet", "\\.net", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
        "tailwind(css)?", "bootstrap", "redux"
    ],
    "Databases & Caches": [
        "postgresql", "postgres", "mysql", "mongodb", "sqlite", "redis", "cassandra",
        "elasticsearch", "dynamodb", "mariadb", "firebase"
    ],
    "DevOps, Cloud & Tools": [
        "git", "github", "docker", "kubernetes", "aws", "azure", "gcp", "linux",
        "ci/cd", "jenkins", "terraform", "nginx", "kafka", "rabbitmq", "postman"
    ],
    "Core CS & Methodologies": [
        "data structures", "algorithms", "dsa", "object-oriented programming", "oops",
        "system design", "operating systems", "dbms", "computer networks",
        "rest(ful)? apis?", "graphql", "microservices", "agile", "unit testing"
    ]
}

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract raw text from PDF bytes using pypdf or pdfplumber fallback."""
    text_content = ""
    # Try pypdf first
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(pdf_bytes))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_content += page_text + "\n"
    except Exception as e:
        print(f"[ResumeParser] pypdf error: {e}")

    # Fallback or augment with pdfplumber if text is sparse
    if len(text_content.strip()) < 50:
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages:
                    plumber_text = page.extract_text()
                    if plumber_text:
                        text_content += plumber_text + "\n"
        except Exception as e:
            print(f"[ResumeParser] pdfplumber error: {e}")

    return text_content.strip()

def parse_contact_info(text: str) -> Dict[str, str]:
    """Extract email, phone, github, and linkedin links via regex."""
    email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    phone_match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
    github_match = re.search(r"(?:github\.com/)([a-zA-Z0-9-]+)", text, re.IGNORECASE)
    linkedin_match = re.search(r"(?:linkedin\.com/in/)([a-zA-Z0-9-_]+)", text, re.IGNORECASE)

    # Heuristic for name: first non-empty line with letters
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    guessed_name = "Candidate"
    for line in lines[:5]:
        if 2 <= len(line.split()) <= 4 and re.match(r"^[A-Za-z\s.'-]+$", line):
            guessed_name = line
            break

    return {
        "name": guessed_name,
        "email": email_match.group(0) if email_match else "",
        "phone": phone_match.group(0) if phone_match else "",
        "github_handle": github_match.group(1) if github_match else "",
        "linkedin_handle": linkedin_match.group(1) if linkedin_match else ""
    }

def extract_skills_from_text(text: str) -> List[str]:
    """Extract and normalize recognized technical skills from resume text."""
    lower_text = text.lower()
    found_skills = set()

    for category, patterns in TECH_SKILL_PATTERNS.items():
        for pat in patterns:
            # Word boundary regex matching
            regex = rf"(?:\b|_){pat}(?:\b|_)"
            if re.search(regex, lower_text):
                # Clean and standardize skill display name
                clean_name = pat.replace("\\+", "+").replace("\\.", ".").replace("?", "").replace("(css)?", "").replace("(\\.?js)?", "").replace("s?", "")
                display_name = clean_name.capitalize()
                # Special cases
                if display_name in ("Html", "Html5"): display_name = "HTML5"
                elif display_name in ("Css", "Css3"): display_name = "CSS3"
                elif display_name in ("Javascript", "Js"): display_name = "JavaScript"
                elif display_name in ("Typescript", "Ts"): display_name = "TypeScript"
                elif display_name == "Aws": display_name = "AWS"
                elif display_name == "Gcp": display_name = "GCP"
                elif display_name == "Dsa": display_name = "Data Structures & Algorithms"
                elif display_name == "Dbms": display_name = "DBMS"
                elif display_name == "Sql": display_name = "SQL"
                elif display_name == "Rest apis" or display_name == "Rest": display_name = "REST APIs"
                elif display_name == "Graphql": display_name = "GraphQL"
                elif display_name == "Ci/cd": display_name = "CI/CD"
                elif display_name == "Fastapi": display_name = "FastAPI"
                elif display_name == "Postgresql" or display_name == "Postgres": display_name = "PostgreSQL"
                elif display_name == "Mysql": display_name = "MySQL"
                elif display_name == "Mongodb": display_name = "MongoDB"
                found_skills.add(display_name)

    return sorted(list(found_skills))

def extract_projects_and_bullets(text: str) -> List[Dict[str, Any]]:
    """Heuristic extraction of project sections and bullet achievements."""
    projects = []
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    
    in_projects_section = False
    current_project = None

    project_section_headers = ["projects", "personal projects", "academic projects", "key projects"]
    other_section_headers = ["education", "experience", "skills", "certifications", "achievements", "work experience"]

    for line in lines:
        lower = line.lower()
        # Detect start of projects section
        if any(h in lower for h in project_section_headers) and len(line) < 30:
            in_projects_section = True
            continue
        # Detect next section start
        if in_projects_section and any(h in lower for h in other_section_headers) and len(line) < 30:
            in_projects_section = False
            if current_project:
                projects.append(current_project)
                current_project = None
            continue

        if in_projects_section:
            # Bullet point detection
            if line.startswith(("-", "•", "*", "–")) or re.match(r"^\d+\.", line):
                clean_bullet = re.sub(r"^[-•*–\d.]\s*", "", line).strip()
                if current_project:
                    current_project["bullets"].append(clean_bullet)
            elif len(line) < 60 and not line.endswith("."):
                # Likely a project title
                if current_project:
                    projects.append(current_project)
                current_project = {"title": line, "bullets": []}
            elif current_project:
                current_project["bullets"].append(line)

    if current_project:
        projects.append(current_project)

    # Fallback if no projects header found: pick prominent action bullets
    if not projects:
        bullet_lines = [l for l in lines if l.startswith(("-", "•", "*", "–"))]
        if bullet_lines:
            projects.append({
                "title": "Featured Engineering Projects",
                "bullets": [re.sub(r"^[-•*–]\s*", "", b).strip() for b in bullet_lines[:6]]
            })

    return projects

def parse_full_resume(text_or_bytes: Any) -> Dict[str, Any]:
    """Master resume parsing orchestrator returning structured entities."""
    if isinstance(text_or_bytes, bytes):
        raw_text = extract_text_from_pdf(text_or_bytes)
    else:
        raw_text = str(text_or_bytes)

    contact = parse_contact_info(raw_text)
    skills = extract_skills_from_text(raw_text)
    projects = extract_projects_and_bullets(raw_text)

    return {
        "raw_text": raw_text,
        "name": contact["name"],
        "email": contact["email"],
        "phone": contact["phone"],
        "github_handle": contact["github_handle"],
        "linkedin_handle": contact["linkedin_handle"],
        "skills": skills,
        "projects": projects
    }
