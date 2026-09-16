import re
import os
from typing import Dict, Any, List
from pypdf import PdfReader

# Comprehensive canonical skills taxonomy
SKILL_TAXONOMY = {
    "core_languages": [
        "Python", "Java", "C++", "C", "JavaScript", "TypeScript", "Go", "Rust", "C#", "PHP", "Ruby", "Kotlin", "Swift"
    ],
    "frameworks": [
        "React", "Node.js", "Express", "FastAPI", "Django", "Flask", "Spring Boot", "Next.js", "Vue.js", "Angular",
        "Tailwind CSS", "Bootstrap", "Redux", "REST APIs", "GraphQL"
    ],
    "databases": [
        "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite", "Oracle", "Cassandra", "SQL"
    ],
    "tools_devops": [
        "Docker", "Kubernetes", "Git", "GitHub", "AWS", "GCP", "Azure", "Linux", "CI/CD", "Postman", "Nginx"
    ],
    "concepts": [
        "Data Structures", "Algorithms", "OOP", "DBMS", "Operating Systems", "Computer Networks", "System Design", "Microservices"
    ]
}

class ResumeParser:
    """Extracts text and identifies structured technical skills and contact info from resumes."""

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        try:
            reader = PdfReader(pdf_path)
            text_parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            return "\n".join(text_parts)
        except Exception as e:
            print(f"[ResumeParser] PDF extraction error: {e}")
            return ""

    def parse(self, raw_text: str) -> Dict[str, Any]:
        if not raw_text:
            return self._empty_result()

        email = self._extract_email(raw_text)
        phone = self._extract_phone(raw_text)
        name = self._extract_name(raw_text)
        extracted_skills = self._extract_skills(raw_text)

        all_flat_skills = []
        for cat_skills in extracted_skills.values():
            all_flat_skills.extend(cat_skills)

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "skills": extracted_skills,
            "all_skills": list(set(all_flat_skills)),
            "skills_count": len(set(all_flat_skills)),
            "text_snippet": raw_text[:500] + ("..." if len(raw_text) > 500 else "")
        }

    def _extract_email(self, text: str) -> str:
        match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
        return match.group(0) if match else ""

    def _extract_phone(self, text: str) -> str:
        match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
        return match.group(0) if match else ""

    def _extract_name(self, text: str) -> str:
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        for line in lines[:5]:
            if len(line.split()) in (2, 3, 4) and not re.search(r"[@\d:]", line):
                # Basic name heuristic
                return line
        return "Engineering Candidate"

    def _extract_skills(self, text: str) -> Dict[str, List[str]]:
        results: Dict[str, List[str]] = {
            "core_languages": [],
            "frameworks": [],
            "databases": [],
            "tools_devops": [],
            "concepts": []
        }
        
        lower_text = text.lower()
        
        for category, skills in SKILL_TAXONOMY.items():
            for skill in skills:
                # Word boundary match
                pattern = r"\b" + re.escape(skill.lower()) + r"\b"
                if re.search(pattern, lower_text):
                    results[category].append(skill)
                    
        return results

    def _empty_result(self) -> Dict[str, Any]:
        return {
            "name": "Candidate",
            "email": "",
            "phone": "",
            "skills": {k: [] for k in SKILL_TAXONOMY},
            "all_skills": [],
            "skills_count": 0,
            "text_snippet": ""
        }

resume_parser = ResumeParser()

