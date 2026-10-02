import os
import sys

# Ensure root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server.utils.resume_parser import parse_contact_info, parse_full_resume

def test_auto_extraction():
    sample_text = """
    PRIYA SUNDARAM
    priya.sundaram@vit.ac.in | +91 9845012345 | Chennai, India
    GitHub: https://github.com/priya-codes | LeetCode: https://leetcode.com/u/priya_algo | LinkedIn: linkedin.com/in/priya-sundaram

    EDUCATION
    B.Tech Computer Science & Engineering (2022 - 2026) - CGPA: 9.1/10

    SKILLS
    Python, FastAPI, Docker, PostgreSQL, React, Git, Redis

    PROJECTS
    1. Distributed Cloud Task Queue
    - Built task scheduling service with Redis and Celery handling 1,000 tasks/min.
    """

    contact = parse_contact_info(sample_text)
    print("Parsed Contact:", contact)

    assert contact["name"] == "Priya Sundaram", f"Expected 'Priya Sundaram', got '{contact['name']}'"
    assert contact["email"] == "priya.sundaram@vit.ac.in", f"Expected email, got '{contact['email']}'"
    assert "9845012345" in contact["phone"], f"Expected phone with 9845012345, got '{contact['phone']}'"
    assert contact["github_handle"] == "priya-codes", f"Expected 'priya-codes', got '{contact['github_handle']}'"
    assert contact["leetcode_handle"] == "priya_algo", f"Expected 'priya_algo', got '{contact['leetcode_handle']}'"
    assert contact["linkedin_handle"] == "priya-sundaram", f"Expected 'priya-sundaram', got '{contact['linkedin_handle']}'"

    full = parse_full_resume(sample_text)
    assert len(full["skills"]) >= 5, f"Expected at least 5 skills, got {len(full['skills'])}"
    assert full["github_handle"] == "priya-codes"
    assert full["leetcode_handle"] == "priya_algo"

    print("ALL RESUME EXTRACTION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_auto_extraction()
