import re
import io
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional
from server.utils.ai_config import call_llm, extract_json_from_llm, sanitize_log_message

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
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(pdf_bytes))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_content += page_text + "\n"
    except Exception as e:
        print(f"[ResumeParser] pypdf error: {e}")

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


def extract_text_from_docx(docx_bytes: bytes) -> str:
    """Extract raw text from DOCX bytes using python-docx or native zipfile XML parser."""
    # 1. Try python-docx if installed
    try:
        import docx  # type: ignore
        doc = docx.Document(io.BytesIO(docx_bytes))
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text and p.text.strip()]
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    paragraphs.append(row_text)
        if paragraphs:
            return "\n".join(paragraphs)
    except Exception:
        pass

    # 2. Native Python standard library DOCX XML extraction (word/document.xml)
    try:
        with zipfile.ZipFile(io.BytesIO(docx_bytes)) as zf:
            if "word/document.xml" not in zf.namelist():
                return ""
            xml_bytes = zf.read("word/document.xml")
            root = ET.fromstring(xml_bytes)
            ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            lines = []
            for para in root.findall(".//w:p", ns):
                texts = [node.text for node in para.findall(".//w:t", ns) if node.text]
                line = "".join(texts).strip()
                if line:
                    lines.append(line)
            return "\n".join(lines)
    except Exception as e:
        print(f"[ResumeParser] DOCX extraction error: {e}")
        return ""


def extract_raw_text_from_file(content_or_bytes: Any, filename: str = "") -> str:
    """Step 2: Extract raw text from PDF, DOCX, or plain text using Python libraries."""
    if isinstance(content_or_bytes, str):
        return content_or_bytes.strip()

    if isinstance(content_or_bytes, bytes):
        fname_low = (filename or "").lower()
        # Check DOCX by extension or ZIP/OOXML magic header (PK\x03\x04)
        if fname_low.endswith(".docx") or content_or_bytes[:4] == b"PK\x03\x04":
            docx_text = extract_text_from_docx(content_or_bytes)
            if docx_text:
                return docx_text
        # Check PDF by extension or %PDF magic header
        if fname_low.endswith(".pdf") or content_or_bytes[:4] == b"%PDF":
            pdf_text = extract_text_from_pdf(content_or_bytes)
            if pdf_text:
                return pdf_text
        # Fallback UTF-8 decode
        return content_or_bytes.decode("utf-8", errors="ignore").strip()

    return str(content_or_bytes).strip()


def parse_contact_info(text: str) -> Dict[str, str]:
    """
    Extract candidate full name, email, phone, github handle, leetcode handle,
    linkedin handle, and portfolio link via regex and heuristics.
    """
    email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    email = email_match.group(0).strip() if email_match else ""

    phone_match = re.search(
        r"(?:\+?91[\-\s]?)?[6-9]\d{4}[\s\-]?\d{5}|\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}",
        text
    )
    phone = phone_match.group(0).strip() if phone_match else ""

    github_handle = ""
    gh_match = re.search(r"(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_-]+)", text, re.IGNORECASE)
    if not gh_match:
        gh_match = re.search(r"(?:github\s*:\s*@?)([a-zA-Z0-9_-]+)", text, re.IGNORECASE)
    if gh_match:
        cand = gh_match.group(1).strip()
        if cand.lower() not in ("features", "explore", "topics", "trending", "http", "https", "developer", "none"):
            github_handle = cand

    leetcode_handle = ""
    lc_match = re.search(r"(?:https?://)?(?:www\.)?leetcode\.com/(?:u/)?([a-zA-Z0-9_-]+)", text, re.IGNORECASE)
    if not lc_match:
        lc_match = re.search(r"(?:leetcode\s*:\s*@?)([a-zA-Z0-9_-]+)", text, re.IGNORECASE)
    if lc_match:
        cand = lc_match.group(1).strip()
        if cand.lower() not in ("problems", "contest", "explore", "http", "https", "developer", "none"):
            leetcode_handle = cand

    linkedin_handle = ""
    li_match = re.search(r"(?:https?://)?(?:www\.)?linkedin\.com/in/([a-zA-Z0-9_-]+)", text, re.IGNORECASE)
    if not li_match:
        li_match = re.search(r"(?:linkedin\s*:\s*@?)([a-zA-Z0-9_-]+)", text, re.IGNORECASE)
    if li_match:
        cand = li_match.group(1).strip()
        if cand.lower() not in ("http", "https", "in", "developer"):
            linkedin_handle = cand

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    ignore_header_keywords = {
        "resume", "curriculum vitae", "cv", "profile", "software engineer",
        "developer", "contact", "education", "experience", "projects", "skills",
        "summary", "objective", "certifications", "phone", "email", "address"
    }

    guessed_name = "Candidate"
    for line in lines[:8]:
        name_prefix_match = re.search(r"^name\s*:\s*([A-Za-z\s.'-]+)", line, re.IGNORECASE)
        if name_prefix_match:
            candidate_val = name_prefix_match.group(1).strip()
            if 2 <= len(candidate_val.split()) <= 4:
                guessed_name = candidate_val.title() if candidate_val.isupper() else candidate_val
                break

        if "@" in line or "http" in line.lower() or "github" in line.lower() or "linkedin" in line.lower() or "leetcode" in line.lower():
            parts = re.split(r"[|,•–\t]", line)
            first_part = parts[0].strip()
            if first_part.lower() not in ignore_header_keywords and 2 <= len(first_part.split()) <= 4 and re.match(r"^[A-Za-z\s.'-]+$", first_part):
                guessed_name = first_part.title() if first_part.isupper() else first_part
                break
            continue

        cleaned_line = re.sub(r"^[•*–-]\s*", "", line).strip()
        words = cleaned_line.split()
        if 2 <= len(words) <= 4 and cleaned_line.lower() not in ignore_header_keywords and re.match(r"^[A-Za-z\s.'-]+$", cleaned_line):
            if not any(w.lower() in ignore_header_keywords for w in words):
                guessed_name = cleaned_line.title() if cleaned_line.isupper() else cleaned_line
                break

    return {
        "name": guessed_name,
        "email": email,
        "phone": phone,
        "github_handle": github_handle,
        "leetcode_handle": leetcode_handle,
        "linkedin_handle": linkedin_handle
    }


def extract_skills_from_text(text: str) -> List[str]:
    """Extract and normalize recognized technical skills from resume text."""
    lower_text = text.lower()
    found_skills = set()

    for category, patterns in TECH_SKILL_PATTERNS.items():
        for pat in patterns:
            regex = rf"(?:\b|_){pat}(?:\b|_)"
            if re.search(regex, lower_text):
                clean_name = pat.replace("\\+", "+").replace("\\.", ".").replace("?", "").replace("(css)?", "").replace("(\\.?js)?", "").replace("(ful)?", "").replace("s?", "")
                display_name = clean_name.capitalize()
                if display_name in ("Html", "Html5"): display_name = "HTML5"
                elif display_name in ("Css", "Css3"): display_name = "CSS3"
                elif display_name in ("Javascript", "Js"): display_name = "JavaScript"
                elif display_name in ("Typescript", "Ts"): display_name = "TypeScript"
                elif display_name == "Aws": display_name = "AWS"
                elif display_name == "Gcp": display_name = "GCP"
                elif display_name == "Dsa": display_name = "Data Structures & Algorithms"
                elif display_name == "Dbms": display_name = "DBMS"
                elif display_name == "Sql": display_name = "SQL"
                elif display_name in ("Rest api", "Rest apis", "Rest"): display_name = "REST APIs"
                elif display_name == "Graphql": display_name = "GraphQL"
                elif display_name == "Ci/cd": display_name = "CI/CD"
                elif display_name == "Fastapi": display_name = "FastAPI"
                elif display_name in ("Postgresql", "Postgres"): display_name = "PostgreSQL"
                elif display_name == "Mysql": display_name = "MySQL"
                elif display_name == "Mongodb": display_name = "MongoDB"
                elif display_name == "Scikit-learn": display_name = "Scikit-Learn"
                elif display_name == "Node": display_name = "Node.js"
                elif display_name == "React": display_name = "React"
                elif display_name == "Next": display_name = "Next.js"
                found_skills.add(display_name)

    return sorted(list(found_skills))


def extract_education_from_text(text: str) -> List[Dict[str, str]]:
    """Heuristic extraction of candidate education entries."""
    education = []
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    deg_pattern = re.compile(
        r"(B\.?\s*Tech|B\.?\s*E\.?|Bachelor|M\.?\s*Tech|Master|B\.?\s*Sc|M\.?\s*Sc|BCA|MCA|Diploma|Computer Science|Information Technology)",
        re.IGNORECASE
    )
    cgpa_pattern = re.compile(r"(?:CGPA|GPA|Percentage)\s*[:\-]?\s*([0-9.]+(?:\s*/\s*[0-9.]+|%?))", re.IGNORECASE)
    year_pattern = re.compile(r"(20\d{2}\s*[–\-to]+\s*20\d{2}|20\d{2})")

    for i, line in enumerate(lines):
        if deg_pattern.search(line) and len(line) < 120:
            year_match = year_pattern.search(line)
            score_val = ""
            # Check same line or next line for CGPA/GPA
            context_window = line + " " + (lines[i + 1] if i + 1 < len(lines) else "")
            cgpa_m = cgpa_pattern.search(context_window)
            if cgpa_m:
                score_val = cgpa_m.group(1).strip()
            if not year_match and i + 1 < len(lines):
                year_match = year_pattern.search(lines[i + 1])

            education.append({
                "degree": line,
                "institution": lines[i + 1] if (i + 1 < len(lines) and not cgpa_pattern.search(lines[i + 1]) and len(lines[i + 1]) < 80) else "University / Institute",
                "year": year_match.group(1) if year_match else "2022 - 2026",
                "score": score_val
            })
            break

    if not education:
        education.append({
            "degree": "B.Tech in Computer Science & Engineering",
            "institution": "Engineering Institute",
            "year": "2022 - 2026",
            "score": ""
        })
    return education


def extract_experience_from_text(text: str) -> List[Dict[str, Any]]:
    """Heuristic extraction of work/internship experience sections."""
    experiences = []
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    in_exp = False
    current_exp = None

    exp_headers = {"experience", "work experience", "internships", "professional experience", "employment"}
    stop_headers = {"projects", "personal projects", "academic projects", "education", "skills", "technical skills", "certifications", "achievements"}

    for line in lines:
        low = line.lower().rstrip(":")
        if low in exp_headers:
            in_exp = True
            continue
        if in_exp and low in stop_headers:
            if current_exp:
                experiences.append(current_exp)
                current_exp = None
            in_exp = False
            continue

        if in_exp:
            if line.startswith(("-", "•", "*", "–")):
                bullet = re.sub(r"^[-•*–]\s*", "", line).strip()
                if current_exp is None:
                    current_exp = {"role": "Software Engineering Intern", "company": "", "duration": "", "highlights": []}
                current_exp["highlights"].append(bullet)
            elif len(line) < 90:
                if current_exp:
                    experiences.append(current_exp)
                current_exp = {"role": line, "company": "", "duration": "", "highlights": []}

    if current_exp:
        experiences.append(current_exp)
    return experiences


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
        if any(h == lower.rstrip(":") or h in lower for h in project_section_headers) and len(line) < 30:
            in_projects_section = True
            continue
        if in_projects_section and any(h == lower.rstrip(":") or h in lower for h in other_section_headers) and len(line) < 30:
            in_projects_section = False
            if current_project:
                projects.append(current_project)
                current_project = None
            continue

        if in_projects_section:
            if line.startswith(("-", "•", "*", "–")):
                clean_bullet = re.sub(r"^[-•*–]\s*", "", line).strip()
                if current_project:
                    current_project["bullets"].append(clean_bullet)
            elif re.match(r"^\d+\.\s+", line) and len(line) < 85:
                if current_project:
                    projects.append(current_project)
                clean_title = re.sub(r"^\d+\.\s*", "", line).strip()
                current_project = {"title": clean_title, "bullets": []}
            elif len(line) < 65 and not line.endswith("."):
                if current_project:
                    projects.append(current_project)
                current_project = {"title": line, "bullets": []}
            elif current_project:
                current_project["bullets"].append(line)

    if current_project:
        projects.append(current_project)

    if not projects:
        bullet_lines = [l for l in lines if l.startswith(("-", "•", "*", "–"))]
        if bullet_lines:
            projects.append({
                "title": "Featured Engineering Projects",
                "bullets": [re.sub(r"^[-•*–]\s*", "", b).strip() for b in bullet_lines[:6]]
            })

    # Attach detected skills per project as tech_stack
    for proj in projects:
        proj_text = proj.get("title", "") + " " + " ".join(proj.get("bullets", []))
        proj["tech_stack"] = extract_skills_from_text(proj_text)

    return projects


def parse_full_resume(text_or_bytes: Any, filename: str = "") -> Dict[str, Any]:
    """Synchronous deterministic resume parser returning structured candidate JSON."""
    raw_text = extract_raw_text_from_file(text_or_bytes, filename=filename)
    contact = parse_contact_info(raw_text)
    skills = extract_skills_from_text(raw_text)
    education = extract_education_from_text(raw_text)
    experience = extract_experience_from_text(raw_text)
    projects = extract_projects_and_bullets(raw_text)

    return {
        "raw_text": raw_text,
        "name": contact["name"],
        "email": contact["email"],
        "phone": contact["phone"],
        "github_handle": contact["github_handle"],
        "leetcode_handle": contact["leetcode_handle"],
        "linkedin_handle": contact["linkedin_handle"],
        "links": {
            "github_handle": contact["github_handle"],
            "leetcode_handle": contact["leetcode_handle"],
            "linkedin_handle": contact["linkedin_handle"]
        },
        "skills": skills,
        "education": education,
        "experience": experience,
        "projects": projects,
        "structured_by": "Continue without API"
    }


async def structure_resume_with_gemini(text_or_bytes: Any, filename: str = "") -> Dict[str, Any]:
    """
    Step 2 & Step 3:
    1. Extract raw text from PDF or DOCX using Python libraries.
    2. Use Gemini (or configured AI via call_llm) to extract skills, education,
       experience, projects, and links into structured JSON, merging with deterministic
       signals so nothing is ever lost.
    """
    base_parsed = parse_full_resume(text_or_bytes, filename=filename)
    raw_text = base_parsed["raw_text"]
    if not raw_text or len(raw_text.strip()) < 20:
        return base_parsed

    system_prompt = (
        "You are an expert technical resume parser. Extract structured candidate information from the resume text into JSON. "
        "Never invent facts not present in the resume. Return ONLY valid JSON with these exact keys:\n"
        "- 'name': string\n"
        "- 'email': string\n"
        "- 'phone': string\n"
        "- 'skills': list of technical skill strings\n"
        "- 'education': list of objects [{'degree': string, 'institution': string, 'year': string, 'score': string}]\n"
        "- 'experience': list of objects [{'role': string, 'company': string, 'duration': string, 'highlights': list of strings}]\n"
        "- 'projects': list of objects [{'title': string, 'tech_stack': list of strings, 'bullets': list of strings}]\n"
        "- 'links': {'github_handle': string, 'leetcode_handle': string, 'linkedin_handle': string}"
    )

    prompt = f"Resume Text:\n{raw_text[:5000]}"
    llm_out = await call_llm(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=0.1,
        max_tokens=1400,
        caller_name="ResumeStructurer"
    )

    if llm_out:
        ai_data = extract_json_from_llm(llm_out)
        if isinstance(ai_data, dict):
            # Merge AI structured data with deterministic extraction
            ai_links = ai_data.get("links") if isinstance(ai_data.get("links"), dict) else {}
            gh = (ai_links.get("github_handle") or ai_data.get("github_handle") or base_parsed["github_handle"] or "").strip()
            lc = (ai_links.get("leetcode_handle") or ai_data.get("leetcode_handle") or base_parsed["leetcode_handle"] or "").strip()
            li = (ai_links.get("linkedin_handle") or ai_data.get("linkedin_handle") or base_parsed["linkedin_handle"] or "").strip()
            # Clean URL prefixes if LLM returned full URLs for handles
            gh = re.sub(r"^https?://(?:www\.)?github\.com/", "", gh, flags=re.IGNORECASE).strip("/")
            lc = re.sub(r"^https?://(?:www\.)?leetcode\.com/(?:u/)?", "", lc, flags=re.IGNORECASE).strip("/")
            li = re.sub(r"^https?://(?:www\.)?linkedin\.com/in/", "", li, flags=re.IGNORECASE).strip("/")

            ai_skills = [str(s).strip() for s in (ai_data.get("skills") or []) if str(s).strip()]
            merged_skills = sorted(list(set(base_parsed["skills"] + ai_skills)))

            ai_projects = ai_data.get("projects")
            projects = ai_projects if (isinstance(ai_projects, list) and len(ai_projects) > 0) else base_parsed["projects"]

            ai_edu = ai_data.get("education")
            education = ai_edu if (isinstance(ai_edu, list) and len(ai_edu) > 0) else base_parsed["education"]

            ai_exp = ai_data.get("experience")
            experience = ai_exp if isinstance(ai_exp, list) else base_parsed["experience"]

            return {
                "raw_text": raw_text,
                "name": (ai_data.get("name") or base_parsed["name"]).strip(),
                "email": (ai_data.get("email") or base_parsed["email"]).strip(),
                "phone": (ai_data.get("phone") or base_parsed["phone"]).strip(),
                "github_handle": gh,
                "leetcode_handle": lc,
                "linkedin_handle": li,
                "links": {
                    "github_handle": gh,
                    "leetcode_handle": lc,
                    "linkedin_handle": li
                },
                "skills": merged_skills,
                "education": education,
                "experience": experience,
                "projects": projects,
                "structured_by": "AI Powered (Gemini)"
            }

    return base_parsed
