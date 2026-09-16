import os
from server.services.pdf_resume_service import pdf_resume_service

def test_pdf_generation():
    candidate_profile = {
        "full_name": "Aarav Sharma",
        "email": "aarav.sharma@example.com",
        "phone": "+91 98765 43210",
        "preferred_location": "Bangalore, India",
        "github_username": "aarav-sharma",
        "skill_vector": {
            "languages": ["Python", "JavaScript", "SQL", "C++"],
            "frameworks": ["FastAPI", "React", "Node.js"],
            "databases": ["PostgreSQL", "MongoDB", "Redis"],
            "tools": ["Git", "Docker", "Linux"],
            "cs_foundations": ["DSA", "DBMS", "Operating Systems"]
        }
    }

    tailored_data = {
        "company_name": "Flipkart",
        "role_title": "Software Development Engineer - 1 (SDE-1)",
        "summary_statement": "Adaptable and results-driven Software Engineer with proven capability building robust asynchronous APIs and scalable frontend systems.",
        "bullet_rewrites": [
            {
                "original_bullet": "Developed backend APIs and handled database queries.",
                "tailored_bullet": "Architected high-throughput RESTful API endpoints utilizing asynchronous request pipelines, optimizing query execution plans to reduce latency by 28%.",
                "framework": "CAR/STAR"
            },
            {
                "original_bullet": "Created frontend user interface and managed state.",
                "tailored_bullet": "Engineered responsive client interfaces in React with modular state management, accelerating component render cycles and streamlining cross-device user flows.",
                "framework": "CAR/STAR"
            },
            {
                "original_bullet": "Worked with team on deployment and testing.",
                "tailored_bullet": "Implemented automated unit and integration test suites, containerizing core services with Docker to ensure reproducible zero-downtime deployment pipelines.",
                "framework": "CAR/STAR"
            }
        ]
    }

    pdf_bytes = pdf_resume_service.generate_ats_resume_pdf(candidate_profile, tailored_data)
    assert pdf_bytes is not None, "PDF bytes should not be None"
    assert len(pdf_bytes) > 1000, f"PDF bytes should be > 1000 bytes, got {len(pdf_bytes)}"
    assert pdf_bytes[:5] == b"%PDF-", f"PDF header must start with %PDF-, got {pdf_bytes[:5]}"
    print(f"[SUCCESS] Generated ATS Resume PDF: {len(pdf_bytes)} bytes. Verified valid %PDF- header.")

if __name__ == "__main__":
    test_pdf_generation()

