from typing import Dict, List, Any

CURATED_LEARNING_RESOURCES: Dict[str, List[Dict[str, Any]]] = {
    "Spring Boot": [
        {
            "provider": "Official Documentation",
            "title": "Spring Boot Reference Guide & Building a RESTful Web Service",
            "url": "https://spring.io/guides/gs/rest-service/",
            "resource_type": "DOCUMENTATION",
            "cost": "FREE",
            "time_commitment": "2 hours",
            "description": "Production tutorial for bootstrapping REST microservices with Spring Boot."
        },
        {
            "provider": "NPTEL",
            "title": "IIT Kharagpur: Software Engineering & Enterprise Architecture",
            "url": "https://nptel.ac.in/courses",
            "resource_type": "ACADEMIC_COURSE",
            "cost": "FREE",
            "time_commitment": "12 hours",
            "description": "Academic course on design patterns, enterprise layers, and architectural foundations."
        },
        {
            "provider": "YouTube",
            "title": "freeCodeCamp: Full Spring Boot 3 & Spring Security Masterclass",
            "url": "https://www.youtube.com/watch?v=9SGDpan58Hg",
            "resource_type": "PRACTICAL_VIDEO",
            "cost": "FREE",
            "time_commitment": "4 hours",
            "description": "End-to-end hands-on video tutorial covering controllers, JPA, and JWT authentication."
        }
    ],
    "Docker": [
        {
            "provider": "Official Documentation",
            "title": "Docker Get Started — Orientation and Setup",
            "url": "https://docs.docker.com/get-started/",
            "resource_type": "DOCUMENTATION",
            "cost": "FREE",
            "time_commitment": "1.5 hours",
            "description": "Official guide on Dockerfiles, images, containers, and multi-stage builds."
        },
        {
            "provider": "YouTube",
            "title": "TechWorld with Nana: Docker Tutorial for Beginners",
            "url": "https://www.youtube.com/watch?v=3c-iBn73dDE",
            "resource_type": "PRACTICAL_VIDEO",
            "cost": "FREE",
            "time_commitment": "3 hours",
            "description": "Comprehensive visual introduction to containerization, Docker Compose, and networking."
        },
        {
            "provider": "GitHub",
            "title": "awesome-docker: Curated list of Docker resources and examples",
            "url": "https://github.com/veggiemonk/awesome-docker",
            "resource_type": "HANDS_ON",
            "cost": "FREE",
            "time_commitment": "Self-paced",
            "description": "Best-practice templates for containerizing Python, Node.js, and Java apps."
        }
    ],
    "FastAPI": [
        {
            "provider": "Official Documentation",
            "title": "FastAPI Tutorial - User Guide",
            "url": "https://fastapi.tiangolo.com/tutorial/",
            "resource_type": "DOCUMENTATION",
            "cost": "FREE",
            "time_commitment": "3 hours",
            "description": "Gold-standard interactive documentation for building modern Python APIs with Pydantic."
        },
        {
            "provider": "YouTube",
            "title": "freeCodeCamp: Python API Development - Comprehensive Course",
            "url": "https://www.youtube.com/watch?v=0sOvCWFmrtA",
            "resource_type": "PRACTICAL_VIDEO",
            "cost": "FREE",
            "time_commitment": "5 hours",
            "description": "Complete production API build including Postgres, Alembic migrations, and JWT."
        }
    ],
    "React": [
        {
            "provider": "Official Documentation",
            "title": "Quick Start — React.dev",
            "url": "https://react.dev/learn",
            "resource_type": "DOCUMENTATION",
            "cost": "FREE",
            "time_commitment": "2.5 hours",
            "description": "Modern official React documentation focusing on Hooks and functional components."
        },
        {
            "provider": "YouTube",
            "title": "freeCodeCamp: Full Modern React 18 Course",
            "url": "https://www.youtube.com/watch?v=bMknfKXIFA8",
            "resource_type": "PRACTICAL_VIDEO",
            "cost": "FREE",
            "time_commitment": "6 hours",
            "description": "Component design, custom hooks, React Router, and context state management."
        }
    ],
    "Data Structures": [
        {
            "provider": "YouTube",
            "title": "Striver's A2Z DSA Course / TakeUForward Playlist",
            "url": "https://takeuforward.org/strivers-a2z-dsa-course/strivers-a2z-dsa-course-sheet-2/",
            "resource_type": "PRACTICAL_VIDEO",
            "cost": "FREE",
            "time_commitment": "40 hours",
            "description": "The quintessential DSA curriculum for Indian engineering placements and product companies."
        },
        {
            "provider": "NPTEL",
            "title": "IIT Madras: Programming, Data Structures and Algorithms Using Python",
            "url": "https://nptel.ac.in/courses/106106145",
            "resource_type": "ACADEMIC_COURSE",
            "cost": "FREE",
            "time_commitment": "15 hours",
            "description": "Deep academic treatment of asymptotic complexity, trees, graphs, and dynamic programming."
        },
        {
            "provider": "YouTube",
            "title": "NeetCode 150: Core Coding Interview Patterns",
            "url": "https://neetcode.io/practice",
            "resource_type": "HANDS_ON",
            "cost": "FREE",
            "time_commitment": "20 hours",
            "description": "Categorized roadmap with video solutions for every classic coding interview pattern."
        }
    ],
    "SQL": [
        {
            "provider": "NPTEL",
            "title": "IIT Kharagpur: Database Management System (DBMS)",
            "url": "https://nptel.ac.in/courses/106105175",
            "resource_type": "ACADEMIC_COURSE",
            "cost": "FREE",
            "time_commitment": "16 hours",
            "description": "Relational algebra, normalization (1NF-BCNF), ACID transactions, and indexing."
        },
        {
            "provider": "Official Documentation",
            "title": "PostgreSQL Official Tutorial",
            "url": "https://www.postgresql.org/docs/current/tutorial.html",
            "resource_type": "DOCUMENTATION",
            "cost": "FREE",
            "time_commitment": "3 hours",
            "description": "Authoritative guide on complex joins, aggregations, window functions, and query planning."
        }
    ],
    "AWS": [
        {
            "provider": "Official Documentation",
            "title": "AWS Cloud Practitioner Essentials",
            "url": "https://aws.amazon.com/training/digital/aws-cloud-practitioner-essentials/",
            "resource_type": "DOCUMENTATION",
            "cost": "FREE",
            "time_commitment": "6 hours",
            "description": "Free official digital course from AWS on EC2, S3, IAM, and cloud architecture basics."
        },
        {
            "provider": "YouTube",
            "title": "freeCodeCamp: AWS Certified Cloud Practitioner Certification Course",
            "url": "https://www.youtube.com/watch?v=SOTamWNgDKc",
            "resource_type": "PRACTICAL_VIDEO",
            "cost": "FREE",
            "time_commitment": "4 hours",
            "description": "Comprehensive practical breakdown of fundamental AWS building blocks."
        }
    ]
}

def get_resources_for_skill(skill_name: str) -> List[Dict[str, Any]]:
    for key, resources in CURATED_LEARNING_RESOURCES.items():
        if key.lower() in skill_name.lower() or skill_name.lower() in key.lower():
            return resources
            
    # Generic authoritative fallback
    return [
        {
            "provider": "Official Documentation",
            "title": f"Official Guide & Tutorial for {skill_name}",
            "url": f"https://www.google.com/search?q={skill_name.replace(' ', '+')}+official+documentation",
            "resource_type": "DOCUMENTATION",
            "cost": "FREE",
            "time_commitment": "3 hours",
            "description": f"First-party developer documentation and hands-on getting started guide for {skill_name}."
        },
        {
            "provider": "YouTube",
            "title": f"freeCodeCamp: Complete {skill_name} Masterclass for Developers",
            "url": f"https://www.youtube.com/results?search_query=freecodecamp+{skill_name.replace(' ', '+')}",
            "resource_type": "PRACTICAL_VIDEO",
            "cost": "FREE",
            "time_commitment": "4 hours",
            "description": f"Free, community-vetted full tutorial covering fundamental to intermediate {skill_name}."
        }
    ]

