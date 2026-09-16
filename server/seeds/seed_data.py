from datetime import datetime
from server.database import get_jobs_col

INITIAL_JOBS = [
    {
        "title": "Software Development Engineer - 1 (SDE-1)",
        "company": "Swiggy",
        "location": "Bengaluru, Karnataka, India",
        "region": "India",
        "work_mode": "Hybrid",
        "experience_required": "0-1 years (Freshers eligible)",
        "salary_range": "₹14 - 18 LPA",
        "portal": "LinkedIn",
        "apply_url": "https://www.linkedin.com/jobs/view/sde1-swiggy-mock",
        "description": "We are looking for an energetic SDE-1 to join our Consumer Tech platform. You will design, build, and maintain high-throughput microservices handling millions of daily delivery orders. You should have strong fundamentals in Data Structures, Algorithms, and asynchronous backend development in Java or Python.",
        "required_skills": ["Java", "Data Structures", "Algorithms", "SQL", "Spring Boot"],
        "preferred_skills": ["Docker", "Redis", "Kafka", "AWS", "Microservices"],
        "source": "LinkedIn Easy Apply",
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "title": "Junior Backend Developer",
        "company": "Razorpay",
        "location": "Bengaluru, Karnataka, India",
        "region": "India",
        "work_mode": "Hybrid",
        "experience_required": "0-2 years",
        "salary_range": "₹12 - 16 LPA",
        "portal": "Naukri",
        "apply_url": "https://www.naukri.com/job-listings-junior-backend-razorpay-mock",
        "description": "Join our Core Payments team. You will be responsible for creating reliable, low-latency transaction processing APIs. You will work closely with relational and NoSQL databases and participate in automated testing pipelines.",
        "required_skills": ["Python", "FastAPI", "SQL", "PostgreSQL", "REST APIs"],
        "preferred_skills": ["Docker", "Redis", "Git", "CI/CD", "Linux"],
        "source": "Naukri",
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "title": "Associate Full Stack Engineer",
        "company": "PhonePe",
        "location": "Hyderabad, Telangana, India",
        "region": "India",
        "work_mode": "Hybrid",
        "experience_required": "0-1 years (2025/2026 Batch)",
        "salary_range": "₹13 - 17 LPA",
        "portal": "LinkedIn",
        "apply_url": "https://www.linkedin.com/jobs/view/fullstack-phonepe-mock",
        "description": "PhonePe is looking for a versatile Full Stack Engineer to build responsive merchant dashboards and merchant settlement services. You should be comfortable building web interfaces in React and linking them with scalable backend services.",
        "required_skills": ["React", "JavaScript", "TypeScript", "Node.js", "SQL"],
        "preferred_skills": ["MongoDB", "Tailwind CSS", "Docker", "Express", "Git"],
        "source": "LinkedIn Easy Apply",
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "title": "Graduate Trainee Engineer - Cloud & DevOps",
        "company": "Jio Platforms",
        "location": "Navi Mumbai / Pune, India",
        "region": "India",
        "work_mode": "On-site",
        "experience_required": "Fresher",
        "salary_range": "₹6 - 9 LPA",
        "portal": "Naukri",
        "apply_url": "https://www.naukri.com/job-listings-graduate-trainee-jio-mock",
        "description": "Work with India's largest 5G and digital ecosystem platform. You will assist in containerizing microservices, monitoring cloud infrastructure, and writing automated deployment scripts.",
        "required_skills": ["Linux", "Python", "Docker", "Git", "Computer Networks"],
        "preferred_skills": ["Kubernetes", "AWS", "CI/CD", "Nginx", "Bash"],
        "source": "Naukri",
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "title": "Software Engineer (Backend - Python/Go)",
        "company": "Postman",
        "location": "Remote / Bengaluru, India",
        "region": "India",
        "work_mode": "Remote",
        "experience_required": "0-2 years",
        "salary_range": "₹16 - 22 LPA",
        "portal": "Greenhouse",
        "apply_url": "https://boards.greenhouse.io/postman/jobs/mock-swe-backend",
        "description": "Postman empowers 30+ million developers worldwide. As a Backend Engineer, you will build and evolve collaborative API tools, WebSocket infrastructure, and developer ecosystems.",
        "required_skills": ["Python", "REST APIs", "SQL", "Git", "Data Structures"],
        "preferred_skills": ["Go", "Docker", "AWS", "PostgreSQL", "System Design"],
        "source": "Greenhouse ATS",
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "title": "Junior Web Applications Engineer",
        "company": "Freshworks",
        "location": "Chennai / Remote, India",
        "region": "India",
        "work_mode": "Remote",
        "experience_required": "0-1 years",
        "salary_range": "₹8 - 12 LPA",
        "portal": "LinkedIn",
        "apply_url": "https://www.linkedin.com/jobs/view/freshworks-junior-web-mock",
        "description": "Join our Customer Experience engineering group. You will engineer modular UI components and integrate with RESTful endpoints to create delightful customer interfaces.",
        "required_skills": ["React", "JavaScript", "HTML", "CSS", "Git"],
        "preferred_skills": ["TypeScript", "Tailwind CSS", "Redux", "REST APIs", "Node.js"],
        "source": "LinkedIn Easy Apply",
        "created_at": datetime.utcnow().isoformat()
    }
]

async def seed_initial_jobs():
    """Seeds initial jobs if the collection is empty."""
    jobs_col = get_jobs_col()
    count = await jobs_col.count_documents({})
    if count == 0:
        print("[Seed] Seeding initial job postings...")
        for job in INITIAL_JOBS:
            await jobs_col.insert_one(job)
        print(f"[Seed] Successfully seeded {len(INITIAL_JOBS)} jobs.")
    else:
        print(f"[Seed] Jobs collection already has {count} documents.")

